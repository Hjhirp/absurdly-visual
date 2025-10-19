import socketio
import json
import random
from typing import Optional
from ..services.game_service import game_service
from ..services.card_service import card_service
from ..services.video_cache import video_cache
from ..services.ai_service import ai_service
from ..services.supabase_service import supabase_service
from ..services.veo_service import veo_service
from ..models.player import Player, AIPlayer, PlayerType
from ..models.game import GameState
from ..config import settings
import asyncio


def safe_emit_data(data):
    """Convert data to JSON and back to ensure no circular references"""
    try:
        # Force serialization to JSON and back
        json_str = json.dumps(data, default=str)
        return json.loads(json_str)
    except Exception as e:
        print(f"❌ Failed to serialize data: {e}")
        return {}


def register_socket_events(sio: socketio.AsyncServer):
    """Register all Socket.IO event handlers"""
    
    async def handle_ai_player_submission(game_id: str, player_id: str):
        """Handle a single AI player's card submission with 30s delay"""
        game = game_service.get_game(game_id)
        if not game or not game.current_round:
            return
        
        player = game_service.get_player(player_id)
        if not player or player.type != PlayerType.AI:
            return
        
        # Check if already submitted
        has_submitted = any(sub.player_id == player_id for sub in game.current_round.submissions)
        if has_submitted or player_id == game.current_round.czar_id:
            return
        
        # AI submits instantly (no wait time for hackathon demo)
        print(f"🤖 AI player {player.name} selecting cards...")
        
        # Re-check game state after delay
        game = game_service.get_game(game_id)
        if not game or game.state != GameState.PLAYING:
            return
        
        # AI selects cards
        black_card = card_service.get_black_card(game.current_round.black_card_id)
        white_cards = [card_service.get_white_card(cid) for cid in player.hand]
        white_cards_dict = [{"id": c.id, "text": c.text} for c in white_cards if c]
        
        selected_ids = await ai_service.select_cards(
            black_card.text,
            white_cards_dict,
            black_card.pick,
            player.personality if isinstance(player, AIPlayer) else "absurd"
        )
        
        # Submit cards
        if game_service.submit_cards(game_id, player_id, selected_ids):
            await sio.emit('cards_submitted', {
                'player_id': player_id,
                'player_name': player.name,
                'count': len(selected_ids)
            }, room=game_id)
            
            # Send updated game state to all players
            game = game_service.get_game(game_id)
            if game:
                for pid in game.players:
                    p = game_service.get_player(pid)
                    if p and p.socket_id:
                        player_state = game_service.get_game_state_for_player(game_id, pid)
                        await sio.emit('game_state', safe_emit_data(player_state), room=p.socket_id)
    
    async def handle_ai_turns(game_id: str):
        """Handle AI player turns (submissions and judging) - all in parallel"""
        game = game_service.get_game(game_id)
        if not game or not game.current_round:
            return
        
        # Launch all AI player submissions in parallel
        tasks = []
        for player_id in game.players:
            player = game_service.get_player(player_id)
            if player and player.type == PlayerType.AI:
                # Check if already submitted
                has_submitted = any(sub.player_id == player_id for sub in game.current_round.submissions)
                if not has_submitted and player_id != game.current_round.czar_id:
                    # Launch AI submission task (runs in parallel)
                    task = asyncio.create_task(handle_ai_player_submission(game_id, player_id))
                    tasks.append(task)
        
        # Don't wait for tasks to complete - they run in background
        
        # Check if entered judging phase - generate videos for all submissions in parallel
        game = game_service.get_game(game_id)
        if game and game.state == GameState.JUDGING:
            # Start parallel video generation for all submissions
            asyncio.create_task(generate_all_submission_videos(game_id))
            
            czar = game_service.get_player(game.current_round.czar_id)
            if czar and czar.type == PlayerType.AI:
                # AI judges after a delay
                await asyncio.sleep(2)
                
                black_card = card_service.get_black_card(game.current_round.black_card_id)
                submissions_data = []
                for sub in game.current_round.submissions:
                    cards = [card_service.get_white_card(cid) for cid in sub.card_ids]
                    submissions_data.append({
                        "cards": [c.text for c in cards if c]
                    })
                
                winner_index = await ai_service.judge_submissions(
                    black_card.text,
                    submissions_data,
                    czar.personality if isinstance(czar, AIPlayer) else "absurd"
                )
                
                # Select winner
                if game_service.select_winner(game_id, game.current_round.czar_id, winner_index):
                    winner_sub = game.current_round.submissions[winner_index]
                    winner = game_service.get_player(winner_sub.player_id)
                    
                    await sio.emit('winner_selected', {
                        'winner_id': winner_sub.player_id,
                        'winner_name': winner.name,
                        'submission_index': winner_index
                    }, room=game_id)
                    
                    # Send updated game state to all players
                    game = game_service.get_game(game_id)
                    if game:
                        for pid in game.players:
                            p = game_service.get_player(pid)
                            if p and p.socket_id:
                                player_state = game_service.get_game_state_for_player(game_id, pid)
                                await sio.emit('game_state', safe_emit_data(player_state), room=p.socket_id)
                    
                    # Generate video (disabled for now)
                    asyncio.create_task(generate_winner_video(game_id, winner_index))
                    
                    # Auto-advance to next round after delay
                    await asyncio.sleep(5)
                    game = game_service.get_game(game_id)
                    if game and game.state != GameState.GAME_END:
                        game_service.end_round(game_id)
                        
                        # Send new round state to all players
                        game = game_service.get_game(game_id)
                        if game:
                            for pid in game.players:
                                p = game_service.get_player(pid)
                                if p and p.socket_id:
                                    player_state = game_service.get_game_state_for_player(game_id, pid)
                                    await sio.emit('game_state', safe_emit_data(player_state), room=p.socket_id)
                            
                            await sio.emit('round_started', {
                                'round_number': game.current_round.round_number
                            }, room=game_id)
                            
                            # Trigger AI players for new round
                            asyncio.create_task(handle_ai_turns(game_id))
    
    async def generate_all_submission_videos(game_id: str):
        """Generate videos for all submissions in parallel during judging phase"""
        print(f"🎬 Starting parallel video generation for all submissions in game {game_id}")
        game = game_service.get_game(game_id)
        if not game or not game.current_round:
            print(f"❌ Game or round not found")
            return
        
        try:
            black_card = card_service.get_black_card(game.current_round.black_card_id)
            
            # Create tasks for all submissions
            tasks = []
            for idx, submission in enumerate(game.current_round.submissions):
                task = generate_submission_video(game_id, idx, black_card, submission)
                tasks.append(task)
            
            # Run all video generations in parallel
            print(f"🚀 Launching {len(tasks)} parallel video generation tasks")
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Log results
            successful = sum(1 for r in results if r and not isinstance(r, Exception))
            print(f"✅ Completed {successful}/{len(tasks)} video generations")
            
            # Now fetch all video URLs and send to players
            await fetch_and_send_all_videos(game_id)
            
        except Exception as e:
            print(f"❌ Error in parallel video generation: {e}")
            import traceback
            traceback.print_exc()
    
    async def fetch_and_send_all_videos(game_id: str):
        """Fetch all submission videos and send to players"""
        print(f"📹 Fetching all submission videos for game {game_id}")
        game = game_service.get_game(game_id)
        if not game or not game.current_round:
            return
        
        try:
            # Fetch videos for all submissions in parallel
            video_tasks = []
            for idx, submission in enumerate(game.current_round.submissions):
                video_id = getattr(submission, 'video_id', None)
                if video_id:
                    task = wait_for_video_ready(video_id, timeout=settings.VIDEO_FETCH_TIMEOUT)
                    video_tasks.append((idx, task))
                else:
                    video_tasks.append((idx, None))
            
            # Wait for all videos
            video_results = {}
            for idx, task in video_tasks:
                if task:
                    video_url = await task
                    video_results[idx] = video_url
                else:
                    video_results[idx] = settings.VIDEO_PLACEHOLDER_URL
            
            # Send video URLs to all players
            await sio.emit('submission_videos_ready', {
                'videos': video_results
            }, room=game_id)
            
            print(f"✅ Sent {len(video_results)} video URLs to players")
            
        except Exception as e:
            print(f"❌ Error fetching submission videos: {e}")
    
    async def wait_for_video_ready(video_uuid: str, timeout: int = 90) -> Optional[str]:
        """
        Wait for video to be ready in Supabase storage with timeout
        
        Args:
            video_uuid: UUID of the video
            timeout: Maximum seconds to wait (default 90)
            
        Returns:
            Video URL if ready, placeholder URL if timeout/failed
        """
        start_time = asyncio.get_event_loop().time()
        check_interval = 15  # Check every 15 seconds
        
        print(f"⏳ Waiting for video {video_uuid} (timeout: {timeout}s, checking every {check_interval}s)")
        
        while True:
            elapsed = asyncio.get_event_loop().time() - start_time
            
            if elapsed >= timeout:
                print(f"⏱️  Timeout waiting for video {video_uuid} after {timeout}s")
                print(f"🖼️  Using placeholder for failed video")
                return settings.VIDEO_PLACEHOLDER_URL
            
            # Check if video exists in Supabase
            print(f"🔍 Checking Supabase for video {video_uuid} (elapsed: {elapsed:.1f}s)")
            exists = await supabase_service.check_video_exists(video_uuid)
            
            if exists:
                # Video is ready, get URL
                url = await supabase_service.get_video_url_by_uuid(video_uuid)
                if url:
                    print(f"✅ Video ready after {elapsed:.1f}s")
                    return url
            
            # Wait before next check
            print(f"⏳ Video not ready yet, waiting {check_interval}s before next check...")
            await asyncio.sleep(check_interval)
    
    async def generate_submission_video(game_id: str, submission_index: int, black_card, submission):
        """Generate video for a single submission"""
        try:
            # Emit progress: starting
            await sio.emit('video_progress', {
                'game_id': game_id,
                'submission_index': submission_index,
                'status': 'starting',
                'message': 'Starting video generation...'
            }, room=game_id)
            
            white_cards = [card_service.get_white_card(cid) for cid in submission.card_ids]
            white_texts = [c.text for c in white_cards if c]
            
            # Emit progress: generating prompt
            await sio.emit('video_progress', {
                'game_id': game_id,
                'submission_index': submission_index,
                'status': 'prompt',
                'message': 'Creating video prompt...'
            }, room=game_id)
            
            # Generate prompt
            prompt = await ai_service.generate_video_prompt(black_card.text, white_texts)
            
            # Emit progress: generating video
            await sio.emit('video_progress', {
                'game_id': game_id,
                'submission_index': submission_index,
                'status': 'generating',
                'message': 'Generating video with Veo3... (this may take 1-2 minutes)'
            }, room=game_id)
            
            # Generate video directly with Veo3
            import uuid
            
            video_id = str(uuid.uuid4())
            video_url = await veo_service.generate_video(prompt)
            
            result = {
                "video_id": video_id,
                "supabase_url": video_url,
                "message": "Video generated successfully"
            } if video_url else None
            
            if result and result.get("video_id"):
                video_id = result["video_id"]
                supabase_url = result.get("supabase_url")
                print(f"✅ Video ID for submission {submission_index}: {video_id}")
                print(f"📍 Will be available at: {supabase_url}")
                
                # Store video_id with submission (we'll fetch URL later when needed)
                if not hasattr(submission, 'video_id'):
                    submission.video_id = video_id
                
                return video_id
            else:
                print(f"❌ Failed to generate video for submission {submission_index}")
                return None
                
        except Exception as e:
            print(f"❌ Error generating video for submission {submission_index}: {e}")
            return None
    
    async def generate_winner_video(game_id: str, submission_index: int):
        """Fetch winner video from Supabase (already generated during judging)"""
        print(f"🎬 Fetching winner video for game {game_id}")
        game = game_service.get_game(game_id)
        if not game or not game.current_round:
            print(f"❌ Game or round not found")
            return
        
        try:
            submission = game.current_round.submissions[submission_index]
            
            # Check if video_id was stored during parallel generation
            video_id = getattr(submission, 'video_id', None)
            
            if video_id:
                print(f"📹 Found video ID: {video_id}")
                
                # Wait for video to be ready with timeout
                video_url = await wait_for_video_ready(video_id, timeout=settings.VIDEO_FETCH_TIMEOUT)
                
                if video_url:
                    print(f"✅ Video URL retrieved: {video_url}")
                    
                    # Get card data for metadata
                    black_card = card_service.get_black_card(game.current_round.black_card_id)
                    white_cards = [card_service.get_white_card(cid) for cid in submission.card_ids]
                    white_texts = [c.text for c in white_cards if c]
                    
                    # Save video metadata to Supabase
                    winner = game_service.get_player(submission.player_id)
                    video_data = {
                        "black_card_text": black_card.text,
                        "white_card_texts": white_texts,
                        "video_url": video_url,
                        "prompt": "",  # Prompt was sanitized during generation
                        "game_id": game_id,
                        "winner_id": submission.player_id,
                        "winner_name": winner.name if winner else "Unknown"
                    }
                    
                    db_video_id = await supabase_service.save_video(video_data)
                    if db_video_id:
                        print(f"✅ Video metadata saved to Supabase: {db_video_id}")
                        
                        # Copy winning video to winning-videos bucket for feed
                        winning_url = await supabase_service.copy_to_winning_bucket(video_id, db_video_id)
                        if winning_url:
                            print(f"🎉 Winning video added to feed: {winning_url}")
                    
                    # Update game state with video URL
                    game.current_round.video_url = video_url
                    
                    # Notify all players
                    await sio.emit('video_ready', {
                        'video_url': video_url,
                        'video_id': video_id
                    }, room=game_id)
                    
                    # Send updated game state
                    for pid in game.players:
                        p = game_service.get_player(pid)
                        if p and p.socket_id:
                            player_state = game_service.get_game_state_for_player(game_id, pid)
                            await sio.emit('game_state', safe_emit_data(player_state), room=p.socket_id)
                else:
                    print(f"⚠️  Video not ready yet, will retry...")
            else:
                print(f"⚠️  No video ID found for submission {submission_index}")
                
        except Exception as e:
            print(f"❌ Error generating video: {e}")
            import traceback
            traceback.print_exc()
    
    @sio.event
    async def connect(sid, environ):
        """Handle client connection"""
        print(f"Client connected: {sid}")
        await sio.emit('connected', {'sid': sid}, room=sid)
    
    @sio.event
    async def disconnect(sid):
        """Handle client disconnection"""
        print(f"Client disconnected: {sid}")
        
        # Find and disconnect player
        for player in game_service.players.values():
            if player.socket_id == sid:
                player.is_connected = False
                
                # Find their game and notify others
                for game in game_service.games.values():
                    if player.id in game.players:
                        await sio.emit('player_left', {
                            'player_id': player.id,
                            'player_name': player.name
                        }, room=game.id)
                        
                        # Check if all human players have left
                        human_players_connected = any(
                            game_service.get_player(pid) and 
                            game_service.get_player(pid).type == PlayerType.HUMAN and
                            game_service.get_player(pid).is_connected
                            for pid in game.players
                        )
                        
                        # If no human players left, clean up the game
                        if not human_players_connected:
                            print(f"🗑️  No human players left in game {game.id}, cleaning up...")
                            # Remove all players from this game
                            for pid in list(game.players):
                                if pid in game_service.players:
                                    del game_service.players[pid]
                            # Remove the game
                            if game.id in game_service.games:
                                del game_service.games[game.id]
                            print(f"✅ Game {game.id} cleaned up")
                        
                        break
    
    @sio.event
    async def create_game(sid, data):
        """Create a new game"""
        try:
            player_name = data.get('player_name', 'Player')
            settings = data.get('settings', {})
            
            # Create player
            player = Player(name=player_name, socket_id=sid)
            game_service.players[player.id] = player
            
            # Create game
            game = game_service.create_game(player.id, settings)
            
            # Join socket room
            await sio.enter_room(sid, game.id)
            
            # Send game state
            game_state = game_service.get_game_state_for_player(game.id, player.id)
            await sio.emit('game_created', safe_emit_data({
                'game_id': str(game.id),
                'player_id': str(player.id),
                'game_state': game_state
            }), room=sid)
            
        except Exception as e:
            await sio.emit('error', {'message': str(e)}, room=sid)
    
    @sio.event
    async def join_game(sid, data):
        """Join an existing game"""
        try:
            game_id = data.get('game_id')
            player_name = data.get('player_name', 'Player')
            is_ai = data.get('is_ai', False)
            
            game = game_service.get_game(game_id)
            if not game:
                await sio.emit('error', {'message': 'Game not found'}, room=sid)
                return
            
            # Create player
            if is_ai:
                player = AIPlayer(name=player_name, socket_id=sid)
            else:
                player = Player(name=player_name, socket_id=sid)
            
            # Add to game
            if not game_service.add_player(game_id, player):
                await sio.emit('error', {'message': 'Cannot join game'}, room=sid)
                return
            
            # Join socket room
            await sio.enter_room(sid, game_id)
            
            # Notify all players with simple data - only primitives
            player_data = {
                'id': str(player.id),
                'name': str(player.name),
                'type': 'human',
                'score': 0,
                'is_connected': True,
                'card_count': 0
            }
            await sio.emit('player_joined', safe_emit_data({'player': player_data}), room=game_id)
            
            # Send game state to new player (similar to game_created)
            game_state = game_service.get_game_state_for_player(game_id, player.id)
            await sio.emit('game_joined', safe_emit_data({
                'game_id': str(game_id),
                'player_id': str(player.id),
                'game_state': game_state
            }), room=sid)
            
        except Exception as e:
            await sio.emit('error', {'message': str(e)}, room=sid)
    
    @sio.event
    async def start_game(sid, data):
        """Start the game"""
        try:
            game_id = data.get('game_id')
            
            if game_service.start_game(game_id):
                game = game_service.get_game(game_id)
                
                # Send updated state to all players
                for player_id in game.players:
                    player_state = game_service.get_game_state_for_player(game_id, player_id)
                    player = game_service.get_player(player_id)
                    if player and player.socket_id:
                        await sio.emit('game_state', player_state, room=player.socket_id)
                
                await sio.emit('round_started', {
                    'round_number': game.current_round.round_number
                }, room=game_id)
                
                # Trigger AI players to submit cards
                asyncio.create_task(handle_ai_turns(game_id))
            else:
                await sio.emit('error', {'message': 'Cannot start game'}, room=sid)
                
        except Exception as e:
            await sio.emit('error', {'message': str(e)}, room=sid)
    
    @sio.event
    async def submit_cards(sid, data):
        """Submit white cards for the round"""
        try:
            game_id = data.get('game_id')
            player_id = data.get('player_id')
            card_ids = data.get('card_ids', [])
            
            if game_service.submit_cards(game_id, player_id, card_ids):
                game = game_service.get_game(game_id)
                player = game_service.get_player(player_id)
                
                # Notify all players
                await sio.emit('cards_submitted', {
                    'player_id': player_id,
                    'player_name': player.name,
                    'count': len(card_ids)
                }, room=game_id)
                
                # If all submitted, trigger AI players and move to judging
                if game.state == "judging":
                    # Send updated state
                    for pid in game.players:
                        player_state = game_service.get_game_state_for_player(game_id, pid)
                        p = game_service.get_player(pid)
                        if p and p.socket_id:
                            await sio.emit('game_state', player_state, room=p.socket_id)
                    
                    await sio.emit('judging_phase', {}, room=game_id)
                    
                    # Trigger AI czar to judge
                    asyncio.create_task(handle_ai_turns(game_id))
                else:
                    # Trigger remaining AI players to submit
                    asyncio.create_task(handle_ai_turns(game_id))
            else:
                await sio.emit('error', {'message': 'Cannot submit cards'}, room=sid)
                
        except Exception as e:
            await sio.emit('error', {'message': str(e)}, room=sid)
    
    @sio.event
    async def select_winner(sid, data):
        """Czar selects the winning submission"""
        try:
            game_id = data.get('game_id')
            czar_id = data.get('player_id')
            winning_index = data.get('winning_submission')
            
            game = game_service.get_game(game_id)
            
            if game_service.select_winner(game_id, czar_id, winning_index):
                game = game_service.get_game(game_id)
                winning_submission = game.current_round.submissions[winning_index]
                winner = game_service.get_player(winning_submission.player_id)
                
                # Notify all players
                await sio.emit('winner_selected', {
                    'winner_id': winning_submission.player_id,
                    'winner_name': winner.name,
                    'submission_index': winning_index
                }, room=game_id)
                
                # Generate video asynchronously
                asyncio.create_task(generate_winner_video(game_id, winning_index))
                
                # Update game state for all players
                for pid in game.players:
                    player_state = game_service.get_game_state_for_player(game_id, pid)
                    p = game_service.get_player(pid)
                    if p and p.socket_id:
                        await sio.emit('game_state', safe_emit_data(player_state), room=p.socket_id)
                
                # Auto-advance after delay
                await asyncio.sleep(5)
                game = game_service.get_game(game_id)
                if game and game.state != GameState.GAME_END:
                    game_service.end_round(game_id)
                    
                    # Send new round state
                    game = game_service.get_game(game_id)
                    if game:
                        for pid in game.players:
                            player_state = game_service.get_game_state_for_player(game_id, pid)
                            p = game_service.get_player(pid)
                            if p and p.socket_id:
                                await sio.emit('game_state', safe_emit_data(player_state), room=p.socket_id)
                        
                        await sio.emit('round_started', {
                            'round_number': game.current_round.round_number
                        }, room=game_id)
                        
                        # Trigger AI players for new round
                        asyncio.create_task(handle_ai_turns(game_id))
            else:
                await sio.emit('error', {'message': 'Cannot select winner'}, room=sid)
                
        except Exception as e:
            await sio.emit('error', {'message': str(e)}, room=sid)
    
    @sio.event
    async def request_ai_join(sid, data):
        """Request an AI player to join the game"""
        try:
            print(f"🤖 AI join request from {sid}")
            game_id = data.get('game_id')
            personality = data.get('personality', 'absurd')
            
            print(f"🤖 Adding AI to game {game_id}")
            ai_player = game_service.add_ai_player(game_id, personality)
            
            if ai_player:
                print(f"🤖 AI player created: {ai_player.name} ({ai_player.id})")
                
                # Create SIMPLE dict with only strings and numbers
                simple_data = {
                    'player': {
                        'id': str(ai_player.id),
                        'name': str(ai_player.name),
                        'type': 'ai',
                        'score': 0,
                        'is_connected': True,
                        'card_count': 0
                    }
                }
                
                print(f"🤖 Emitting player_joined: {simple_data}")
                await sio.emit('player_joined', simple_data, room=game_id)
                print(f"✅ AI player joined successfully")
            else:
                print(f"❌ Failed to add AI player")
                await sio.emit('error', {'message': 'Cannot add AI player'}, room=sid)
                
        except Exception as e:
            print(f"❌ Exception in request_ai_join: {e}")
            import traceback
            traceback.print_exc()
            await sio.emit('error', {'message': str(e)}, room=sid)
    
    @sio.event
    async def send_message(sid, data):
        """Send chat message"""
        try:
            game_id = data.get('game_id')
            player_id = data.get('player_id')
            message = data.get('message')
            
            player = game_service.get_player(player_id)
            if player:
                await sio.emit('chat_message', {
                    'player_id': player_id,
                    'player_name': player.name,
                    'message': message,
                    'timestamp': data.get('timestamp')
                }, room=game_id)
                
        except Exception as e:
            await sio.emit('error', {'message': str(e)}, room=sid)
