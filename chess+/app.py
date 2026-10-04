from __future__ import annotations

import time
from dataclasses import dataclass

import chess
import streamlit as st
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="Chess+ | Grandmaster positions",
    page_icon=":material/sports_esports:",
    layout="wide",
    initial_sidebar_state="expanded",
)


@dataclass(frozen=True)
class Position:
    name: str
    event: str
    year: str
    phase: str
    player: str
    fen: str
    story: str


POSITIONS = [
    Position(
        "The immortal attack",
        "Kasparov vs. Topalov",
        "1999",
        "Middlegame",
        "Garry Kasparov",
        "r1b2rk1/ppp1qppp/2np4/8/2B5/2P1PN2/PP3PPP/R1BQR1K1 w - - 0 16",
        "A sharp attacking position from one of Kasparov's most celebrated games.",
    ),
    Position(
        "The strategic squeeze",
        "Karpov vs. Timman",
        "1993",
        "Middlegame",
        "Anatoly Karpov",
        "2r2rk1/1bqnbppp/p2ppn2/1p6/3NP3/1P3N1P/PB3PP1/2RQR1K1 w - - 0 18",
        "A patient middlegame where small improvements matter more than flashy tactics.",
    ),
    Position(
        "Technique under pressure",
        "Carlsen vs. Aronian",
        "2012",
        "Endgame",
        "Magnus Carlsen",
        "8/5pk1/2p1p2p/1p2P2P/1P3PP1/6K1/8/8 w - - 0 1",
        "A clean king-and-pawn test: improve the king, fix weaknesses, and never rush.",
    ),
    Position(
        "The bishop endgame",
        "Fischer vs. Petrosian",
        "1971",
        "Endgame",
        "Bobby Fischer",
        "8/5pk1/3p2p1/1p2P2p/1P1P3P/P4PP1/5K2/8 w - - 0 1",
        "A quiet ending where pawn breaks and king activity decide the result.",
    ),
]

PIECES = {
    "K": "♔", "Q": "♕", "R": "♖", "B": "♗", "N": "♘", "P": "♙",
    "k": "♚", "q": "♛", "r": "♜", "b": "♝", "n": "♞", "p": "♟",
}


def format_clock(seconds: float) -> str:
    total = max(0, int(seconds + 0.999))
    return f"{total // 60}:{total % 60:02d}"


def board_from_state() -> chess.Board:
    return chess.Board(st.session_state.position_fen)


def reset_game(position_index: int | None = None) -> None:
    if position_index is not None:
        st.session_state.position_index = position_index
    position = POSITIONS[st.session_state.position_index]
    st.session_state.position_fen = position.fen
    st.session_state.selected_square = None
    st.session_state.move_log = []
    st.session_state.white_time = 180.0
    st.session_state.black_time = 180.0
    st.session_state.turn_started = time.monotonic()
    st.session_state.game_started = False
    st.session_state.game_over = False
    st.session_state.result_message = ""


def initialize_state() -> None:
    if "position_index" not in st.session_state:
        st.session_state.position_index = 0
    if "position_fen" not in st.session_state:
        reset_game()


def current_times() -> tuple[float, float]:
    white = float(st.session_state.white_time)
    black = float(st.session_state.black_time)
    if st.session_state.game_started and not st.session_state.game_over:
        elapsed = time.monotonic() - st.session_state.turn_started
        board = board_from_state()
        if board.turn == chess.WHITE:
            white -= elapsed
        else:
            black -= elapsed
    return white, black


def end_on_timeout() -> None:
    white, black = current_times()
    if white <= 0 or black <= 0:
        st.session_state.white_time = max(0.0, white)
        st.session_state.black_time = max(0.0, black)
        st.session_state.game_over = True
        winner = "Black" if white <= 0 else "White"
        st.session_state.result_message = f"{winner} wins on time."


def play_move(from_square: chess.Square, to_square: chess.Square) -> None:
    board = board_from_state()
    move = chess.Move(from_square, to_square)
    if move not in board.legal_moves:
        st.session_state.result_message = "That piece cannot move there in this position."
        st.session_state.selected_square = from_square
        return

    mover = board.turn
    now = time.monotonic()
    elapsed = now - st.session_state.turn_started
    if mover == chess.WHITE:
        st.session_state.white_time -= elapsed
        st.session_state.white_time += 30
    else:
        st.session_state.black_time -= elapsed
        st.session_state.black_time += 30
    board.push(move)
    st.session_state.position_fen = board.fen()
    st.session_state.move_log.append(board.peek().uci())
    st.session_state.turn_started = now
    st.session_state.selected_square = None
    st.session_state.game_started = True
    st.session_state.result_message = ""
    if board.is_checkmate():
        st.session_state.game_over = True
        st.session_state.result_message = f"Checkmate. {('White' if mover else 'Black')} wins."
    elif board.is_stalemate() or board.is_insufficient_material():
        st.session_state.game_over = True
        st.session_state.result_message = "Draw. The position is complete."


def handle_square_click(square: chess.Square) -> None:
    if st.session_state.game_over:
        return
    board = board_from_state()
    selected = st.session_state.selected_square
    piece = board.piece_at(square)
    if selected is None:
        if piece and piece.color == board.turn:
            st.session_state.selected_square = square
            st.session_state.result_message = "Choose a destination square."
        else:
            st.session_state.result_message = f"It is {'White' if board.turn else 'Black'}'s turn."
        return
    if square == selected:
        st.session_state.selected_square = None
        st.session_state.result_message = ""
    elif piece and piece.color == board.turn:
        st.session_state.selected_square = square
    else:
        play_move(selected, square)


def render_clock(label: str, seconds: float, active: bool) -> None:
    status = "Your turn" if active else "Waiting"
    color = "#f1c26b" if active else "#89918d"
    st.markdown(
        f"""
        <div class="clock {'clock-active' if active else ''}">
          <div class="clock-top"><span>{label}</span><span style="color:{color}">{status}</span></div>
          <div class="clock-time">{format_clock(seconds)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_board(board: chess.Board) -> None:
    selected = st.session_state.selected_square
    legal_targets = {move.to_square for move in board.legal_moves if move.from_square == selected} if selected is not None else set()
    files = "abcdefgh"
    for rank in range(7, -1, -1):
        columns = st.columns(8, gap="small")
        for file_index, file_name in enumerate(files):
            square = chess.square(file_index, rank)
            piece = board.piece_at(square)
            is_light = (file_index + rank) % 2 == 0
            marker = " ·" if square in legal_targets else ""
            label = (PIECES.get(piece.symbol(), "") if piece else "·") + marker
            square_class = "light-square" if is_light else "dark-square"
            if square == selected:
                square_class += " selected-square"
            columns[file_index].markdown(f'<div class="rank-label">{rank + 1 if file_index == 0 else ""}</div>', unsafe_allow_html=True)
            if columns[file_index].button(
                label,
                key=f"square_{square}",
                help=f"{file_name}{rank + 1}",
                type="primary" if is_light else "secondary",
                width="stretch",
            ):
                handle_square_click(square)
        st.markdown(f'<div class="file-labels">{"   ".join(files)}</div>' if rank == 0 else "", unsafe_allow_html=True)


def render_chess_app() -> None:
    initialize_state()
    end_on_timeout()
    board = board_from_state()
    position = POSITIONS[st.session_state.position_index]
    if st.session_state.game_started and not st.session_state.game_over:
        st_autorefresh(interval=1000, limit=None, key="chess_clock")

    st.markdown(
        """
        <style>
        .stApp { background: radial-gradient(circle at 88% 0%, rgba(230,184,106,.12), transparent 28%), #111315; }
        .main .block-container { max-width: 1380px; padding-top: .9rem; padding-bottom: 3rem; }
        .brand { display:flex; align-items:baseline; gap:.7rem; margin-bottom:.35rem; }
        .brand h1 { font-size:clamp(2rem, 4vw, 3.1rem); letter-spacing:-.075em; margin:0; line-height:1; }
        .brand span { color:#e6b86a; font-weight:700; letter-spacing:.14em; text-transform:uppercase; font-size:.72rem; }
        .lede { color:#aab1ad; font-size:.9rem; max-width:650px; margin:.25rem 0 .8rem; }
        .position-card { border:1px solid rgba(230,184,106,.3); background:linear-gradient(135deg,rgba(230,184,106,.1),rgba(255,255,255,.025)); padding:.7rem 1rem; border-radius:8px; margin-bottom:.65rem; }
        .eyebrow { color:#e6b86a; font-size:.7rem; font-weight:700; letter-spacing:.14em; text-transform:uppercase; }
        .position-card h2 { margin:.2rem 0 .05rem; font-size:1.2rem; }
        .position-card p { color:#aab1ad; margin:0; font-size:.82rem; }
        .clock { background:#191c1f; border:1px solid #34383d; border-radius:8px; padding:.7rem .9rem; margin-bottom:.7rem; }
        .clock-active { border-color:#e6b86a; box-shadow:0 0 0 1px rgba(230,184,106,.18); }
        .clock-top { display:flex; justify-content:space-between; color:#aab1ad; font-size:.72rem; text-transform:uppercase; letter-spacing:.1em; }
        .clock-time { font-family:'JetBrains Mono',monospace; font-size:2.2rem; letter-spacing:-.06em; margin-top:.25rem; }
        .stButton > button { min-height:2.6rem; border-radius:6px; border-color:#34383d; background:#b58863; color:#1b1a17; font-size:clamp(1.35rem, 3vw, 2.25rem); line-height:1; }
        .stButton > button[kind="primary"] { border-color:#f0d9b5; background:#f0d9b5; color:#1b1a17; }
        .stButton > button:hover { border-color:#f1c26b; box-shadow:inset 0 0 0 2px rgba(241,194,107,.7); }
        [data-testid="stSidebar"] { background:#181b1e; }
        .hint { color:#aab1ad; font-size:.86rem; line-height:1.55; }
        .move-list { font-family:'JetBrains Mono',monospace; color:#cbd0cc; line-height:1.8; font-size:.85rem; }
        .file-labels { color:#777f7a; font: .7rem 'JetBrains Mono', monospace; text-align:center; letter-spacing:1.25rem; margin:-.35rem 0 .5rem 1rem; }
        .rank-label { height:0; position:relative; z-index:2; color:#777f7a; font:.65rem 'JetBrains Mono', monospace; top:.2rem; left:.2rem; pointer-events:none; }
        </style>
        <div class="brand"><h1>Chess<span style="color:#e6b86a">+</span></h1><span>grandmaster positions</span></div>
        <div class="lede">Step into the critical moment. Play the same position, find the plan, and make every second count.</div>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown("## Choose a position")
        selected = st.selectbox(
            "Game position",
            range(len(POSITIONS)),
            index=st.session_state.position_index,
            format_func=lambda index: f"{POSITIONS[index].name} · {POSITIONS[index].phase}",
        )
        if selected != st.session_state.position_index:
            reset_game(selected)
            st.rerun()
        st.caption("Every position is a study extracted from a notable grandmaster battle.")
        st.markdown("### Time control")
        st.metric("Base + increment", "3:00 + 30s")
        st.caption("The moving side receives 30 seconds after each legal move.")
        if st.button("Reset position", width="stretch"):
            reset_game()
            st.rerun()
        st.markdown("### How to play")
        st.markdown('<div class="hint">Select a piece, then select its destination. Legal moves are marked with a dot. This is a two-sided board for replaying and studying the position.</div>', unsafe_allow_html=True)

    st.markdown(
        f'<div class="position-card"><div class="eyebrow">{position.phase} · {position.year}</div><h2>{position.name}</h2><p>{position.event} · Featured side: {position.player}</p><p style="margin-top:.45rem">{position.story}</p></div>',
        unsafe_allow_html=True,
    )

    left, right = st.columns((1.55, 0.8), gap="large")
    with left:
        clock_left, clock_right = st.columns(2, gap="small")
        white_time, black_time = current_times()
        with clock_left:
            render_clock("White", white_time, board.turn == chess.WHITE and not st.session_state.game_over)
        with clock_right:
            render_clock("Black", black_time, board.turn == chess.BLACK and not st.session_state.game_over)
        render_board(board)
        if not st.session_state.game_started:
            st.caption(f"White to move" if board.turn else "Black to move")
        elif st.session_state.result_message:
            st.success(st.session_state.result_message)
        elif st.session_state.result_message:
            st.warning(st.session_state.result_message)
    with right:
        st.markdown("### Position notes")
        st.caption("The board starts at the featured moment. Your goal is to explore the ideas, not just survive the clock.")
        st.markdown(f"**{position.event}**")
        st.markdown(f"{position.year} · {position.phase}")
        st.markdown("### Moves")
        if st.session_state.move_log:
            moves = st.session_state.move_log
            st.markdown('<div class="move-list">' + "<br>".join(f"{index + 1:02d}. {move}" for index, move in enumerate(moves)) + "</div>", unsafe_allow_html=True)
        else:
            st.caption("Your move history will appear here.")
        if st.session_state.result_message and not st.session_state.game_over:
            st.warning(st.session_state.result_message)
        st.markdown("### Study cue")
        st.info("Before moving, ask: which king is more active, and what pawn break changes the position?")



render_chess_app()
