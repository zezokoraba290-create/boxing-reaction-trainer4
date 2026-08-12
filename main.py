import asyncio
import random
import time

import flet as ft
import flet_audio as fta


# =========================================================
# BOXING MOVES
# =========================================================

MOVES = [
    ("Jab", "jab.mp3"),
    ("Cross", "cross.mp3"),
    ("Lead Hook", "lead_hook.mp3"),
    ("Rear Hook", "rear_hook.mp3"),
    ("Lead Uppercut", "lead_uppercut.mp3"),
    ("Rear Uppercut", "rear_uppercut.mp3"),
    ("Slip Right", "slip_right.mp3"),
    ("Slip Left", "slip_left.mp3"),
    ("Roll Right", "roll_right.mp3"),
    ("Roll Left", "roll_left.mp3"),
    ("Pull Back", "pull_back.mp3"),
    ("Step Back", "step_back.mp3"),
    ("Step Left", "step_left.mp3"),
    ("Step Right", "step_right.mp3"),
    ("Pivot Left", "pivot_left.mp3"),
    ("Pivot Right", "pivot_right.mp3"),
    ("Parry", "parry.mp3"),
    ("High Guard", "high_guard.mp3"),
]


# =========================================================
# SESSION DURATIONS
# =========================================================

DURATIONS = [10, 30, 60, 120]


# =========================================================
# DIFFICULTY
#
# الوقت بين كل حركة والحركة التالية
# =========================================================

DIFFICULTIES = {
    "BEGINNER": (1.50, 2.10),
    "EASY":     (1.15, 1.70),
    "NORMAL":   (0.85, 1.30),
    "HARD":     (0.60, 0.95),
    "EXPERT":   (0.40, 0.65),
}


# =========================================================
# COLORS
# =========================================================

RED = "#E53935"
RED_LIGHT = "#FF5252"
RED_DARK = "#B71C1C"

GREEN = "#43A047"

WHITE = "#FFFFFF"

GRAY = "#AAAAAA"


# =========================================================
# MAIN CLASS
# =========================================================

class ReactionTrainer:

    def __init__(self, page: ft.Page):

        self.page = page

        self.running = False

        self.duration = 30

        self.end_time = 0

        self.last_move = ""

        self.session_id = 0

        self.difficulty = "NORMAL"


        # =================================================
        # PAGE
        # =================================================

        page.title = "Boxing Reaction Trainer"

        page.theme_mode = ft.ThemeMode.DARK

        page.bgcolor = "#000000"

        page.padding = 0

        page.spacing = 0

        page.horizontal_alignment = (
            ft.CrossAxisAlignment.CENTER
        )

        page.vertical_alignment = (
            ft.MainAxisAlignment.CENTER
        )


        # =================================================
        # MOVEMENT AUDIO
        # =================================================

        self.audio_players = {}


        for move_name, filename in MOVES:

            audio = fta.Audio(
                src=f"sounds/{filename}",
                autoplay=False,
                volume=1.0,
            )

            self.audio_players[move_name] = audio

            page.services.append(audio)


        # =================================================
        # START + FINISH WHISTLE
        #
        # IMPORTANT:
        # Put 0003963.mp3 in:
        #
        # assets/sounds/0003963.mp3
        # =================================================

        self.start_finish_audio = fta.Audio(
            src="sounds/0003963.mp3",
            autoplay=False,
            volume=1.0,
        )

        page.services.append(
            self.start_finish_audio
        )


        # =================================================
        # TITLE
        # =================================================

        self.title = ft.Text(
            "🥊 BOXING REACTION",
            size=28,
            weight=ft.FontWeight.BOLD,
            color=WHITE,
            text_align=ft.TextAlign.CENTER,
        )


        self.subtitle = ft.Text(
            "REACTION TRAINER",
            size=13,
            weight=ft.FontWeight.BOLD,
            color=RED_LIGHT,
            text_align=ft.TextAlign.CENTER,
        )


        # =================================================
        # STATUS
        # =================================================

        self.status = ft.Text(
            "READY",
            size=14,
            weight=ft.FontWeight.BOLD,
            color=GRAY,
            text_align=ft.TextAlign.CENTER,
        )


        # =================================================
        # TIMER
        # =================================================

        self.timer_text = ft.Text(
            "00:30",
            size=25,
            weight=ft.FontWeight.BOLD,
            color=WHITE,
            text_align=ft.TextAlign.CENTER,
        )


        # =================================================
        # MOVE LABEL
        # =================================================

        self.move_label = ft.Text(
            "NEXT MOVE",
            size=12,
            weight=ft.FontWeight.BOLD,
            color="#999999",
            text_align=ft.TextAlign.CENTER,
        )


        # =================================================
        # CURRENT MOVE
        # =================================================

        self.move_display = ft.Text(
            "READY",
            size=52,
            weight=ft.FontWeight.BOLD,
            color=RED_LIGHT,
            text_align=ft.TextAlign.CENTER,
        )


        # =================================================
        # PROGRESS BAR
        # =================================================

        self.progress = ft.ProgressBar(
            value=0,
            height=6,
            color=RED,
            bgcolor="#333333",
        )


        # =================================================
        # DIFFICULTY TITLE
        # =================================================

        self.difficulty_title = ft.Text(
            "DIFFICULTY",
            size=12,
            weight=ft.FontWeight.BOLD,
            color="#999999",
            text_align=ft.TextAlign.CENTER,
        )


        # =================================================
        # DIFFICULTY BUTTONS
        # =================================================

        self.difficulty_buttons = []


        for level in DIFFICULTIES.keys():

            button = ft.Button(
                content=level,
                width=95,
                height=40,
                bgcolor="#303030",
                color=WHITE,
                on_click=lambda e, l=level:
                    self.set_difficulty(l),
            )

            self.difficulty_buttons.append(
                button
            )


        self.difficulty_row = ft.Row(
            controls=self.difficulty_buttons,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=7,
            wrap=True,
        )


        # =================================================
        # DURATION TITLE
        # =================================================

        self.duration_title = ft.Text(
            "SESSION DURATION",
            size=12,
            weight=ft.FontWeight.BOLD,
            color="#999999",
            text_align=ft.TextAlign.CENTER,
        )


        # =================================================
        # DURATION BUTTONS
        # =================================================

        self.duration_buttons = []


        for seconds in DURATIONS:

            button = ft.Button(
                content=f"{seconds}s",
                width=75,
                height=40,
                bgcolor="#303030",
                color=WHITE,
                on_click=lambda e, s=seconds:
                    self.set_duration(s),
            )

            self.duration_buttons.append(
                button
            )


        self.duration_row = ft.Row(
            controls=self.duration_buttons,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
            wrap=True,
        )


        # =================================================
        # START BUTTON
        # =================================================

        self.start_btn = ft.Button(
            content="START TRAINING",
            icon=ft.Icons.PLAY_ARROW_ROUNDED,
            width=190,
            height=52,
            bgcolor=GREEN,
            color=WHITE,
            on_click=self.start_session,
        )


        # =================================================
        # STOP BUTTON
        # =================================================

        self.stop_btn = ft.Button(
            content="STOP",
            icon=ft.Icons.STOP_ROUNDED,
            width=120,
            height=52,
            bgcolor=RED_DARK,
            color=WHITE,
            disabled=True,
            on_click=self.stop_session,
        )


        # =================================================
        # TEST WHISTLE
        # =================================================

        self.test_btn = ft.Button(
            content="TEST WHISTLE",
            icon=ft.Icons.VOLUME_UP_ROUNDED,
            width=150,
            height=42,
            bgcolor="#303030",
            color=WHITE,
            on_click=self.test_sound,
        )


        # =================================================
        # MOVE CARD
        # =================================================

        self.move_card = ft.Container(

            width=620,

            padding=30,

            border_radius=22,

            bgcolor="#CC101010",

            border=ft.Border.all(
                1,
                "#55FFFFFF",
            ),

            content=ft.Column(

                controls=[

                    self.move_label,

                    ft.Container(
                        height=8
                    ),

                    self.move_display,

                    ft.Container(
                        height=10
                    ),

                    self.progress,

                ],

                horizontal_alignment=(
                    ft.CrossAxisAlignment.CENTER
                ),
            ),
        )


        # =================================================
        # TIMER CARD
        # =================================================

        self.timer_card = ft.Container(

            width=180,

            padding=12,

            border_radius=15,

            bgcolor="#CC111111",

            border=ft.Border.all(
                1,
                "#33FFFFFF",
            ),

            content=ft.Column(

                controls=[

                    ft.Text(
                        "TIME",
                        size=10,
                        color="#888888",
                        weight=ft.FontWeight.BOLD,
                    ),

                    self.timer_text,

                ],

                horizontal_alignment=(
                    ft.CrossAxisAlignment.CENTER
                ),

                spacing=2,
            ),
        )


        # =================================================
        # CONTROLS CARD
        # =================================================

        self.controls_card = ft.Container(

            width=620,

            padding=20,

            border_radius=18,

            bgcolor="#DD151515",

            border=ft.Border.all(
                1,
                "#33FFFFFF",
            ),

            content=ft.Column(

                controls=[

                    self.difficulty_title,

                    ft.Container(
                        height=8
                    ),

                    self.difficulty_row,

                    ft.Container(
                        height=15
                    ),

                    self.duration_title,

                    ft.Container(
                        height=8
                    ),

                    self.duration_row,

                    ft.Container(
                        height=16
                    ),

                    ft.Row(

                        controls=[
                            self.start_btn,
                            self.stop_btn,
                        ],

                        alignment=(
                            ft.MainAxisAlignment.CENTER
                        ),

                        spacing=12,

                        wrap=True,
                    ),

                    ft.Container(
                        height=8
                    ),

                    self.test_btn,

                ],

                horizontal_alignment=(
                    ft.CrossAxisAlignment.CENTER
                ),
            ),
        )


        # =================================================
        # FOOTER
        # =================================================

        self.footer = ft.Text(
            "SHADOWBOXING • FOOTWORK • REACTION",
            size=10,
            color="#777777",
            text_align=ft.TextAlign.CENTER,
        )


        # =================================================
        # HEADER
        # =================================================

        header = ft.Row(

            controls=[

                ft.Text(
                    "🥊",
                    size=30,
                ),

                ft.Column(

                    controls=[
                        self.title,
                        self.subtitle,
                    ],

                    spacing=0,

                    horizontal_alignment=(
                        ft.CrossAxisAlignment.START
                    ),
                ),

            ],

            alignment=(
                ft.MainAxisAlignment.CENTER
            ),

            spacing=8,
        )


        # =================================================
        # MAIN CONTENT
        # =================================================

        content = ft.Column(

            controls=[

                ft.Container(
                    height=10
                ),

                header,

                ft.Container(
                    height=10
                ),

                self.status,

                ft.Container(
                    height=10
                ),

                self.timer_card,

                ft.Container(
                    height=12
                ),

                self.move_card,

                ft.Container(
                    height=12
                ),

                self.controls_card,

                ft.Container(
                    height=12
                ),

                self.footer,

                ft.Container(
                    height=10
                ),

            ],

            horizontal_alignment=(
                ft.CrossAxisAlignment.CENTER
            ),

            scroll=ft.ScrollMode.AUTO,

            expand=True,
        )


        # =================================================
        # BACKGROUND IMAGE
        # =================================================

        background = ft.Container(

            expand=True,

            image=ft.DecorationImage(

                src="ippo.jpg",

                fit=ft.BoxFit.COVER,

                opacity=0.30,
            ),
        )


        # =================================================
        # DARK OVERLAY
        # =================================================

        overlay = ft.Container(

            expand=True,

            bgcolor="#99000000",
        )


        # =================================================
        # STACK
        # =================================================

        app_stack = ft.Stack(

            expand=True,

            controls=[

                background,

                overlay,

                ft.Container(

                    expand=True,

                    padding=15,

                    content=content,
                ),
            ],
        )


        # =================================================
        # ADD TO PAGE
        # =================================================

        page.add(

            ft.SafeArea(

                expand=True,

                content=app_stack,
            )
        )


        # =================================================
        # DEFAULT SETTINGS
        # =================================================

        self.set_difficulty(
            "NORMAL",
            update=False,
        )

        self.set_duration(
            30,
            update=False,
        )

        page.update()


    # =====================================================
    # DIFFICULTY
    # =====================================================

    def set_difficulty(
        self,
        level,
        update=True,
    ):

        if self.running:
            return


        self.difficulty = level


        for button in self.difficulty_buttons:

            if button.content == level:

                button.bgcolor = RED_DARK

            else:

                button.bgcolor = "#303030"


        min_delay, max_delay = (
            DIFFICULTIES[level]
        )


        self.status.value = (
            f"{level} • "
            f"{min_delay:.2f} - "
            f"{max_delay:.2f}s"
        )


        if update:

            self.page.update()


    # =====================================================
    # DURATION
    # =====================================================

    def set_duration(
        self,
        seconds,
        update=True,
    ):

        if self.running:
            return


        self.duration = seconds


        self.timer_text.value = (
            self.format_time(
                seconds
            )
        )


        for button in self.duration_buttons:

            if button.content == f"{seconds}s":

                button.bgcolor = RED_DARK

            else:

                button.bgcolor = "#303030"


        self.status.value = (
            f"{self.difficulty} • "
            f"{seconds} SECOND SESSION"
        )


        if update:

            self.page.update()


    # =====================================================
    # FORMAT TIME
    # =====================================================

    @staticmethod
    def format_time(seconds):

        seconds = max(
            0,
            int(seconds),
        )

        minutes = (
            seconds // 60
        )

        seconds = (
            seconds % 60
        )

        return (
            f"{minutes:02d}:"
            f"{seconds:02d}"
        )


    # =====================================================
    # PLAY WHISTLE
    #
    # Same 0003963.mp3 for start and finish
    # =====================================================

    async def play_whistle(self):

        try:

            await self.start_finish_audio.play()

            print(
                "WHISTLE: OK",
                flush=True,
            )

        except Exception as ex:

            print(
                "WHISTLE ERROR:",
                repr(ex),
                flush=True,
            )


    # =====================================================
    # PLAY MOVEMENT SOUND
    # =====================================================

    async def play_move_sound(
        self,
        move_name,
    ):

        try:

            audio = (
                self.audio_players.get(
                    move_name
                )
            )


            if audio is None:

                return


            print(
                f"AUDIO: {move_name}",
                flush=True,
            )


            await audio.play()


        except Exception as ex:

            print(
                f"AUDIO ERROR "
                f"[{move_name}]:",
                repr(ex),
                flush=True,
            )


    # =====================================================
    # TEST WHISTLE
    # =====================================================

    def test_sound(self, e):

        self.page.run_task(
            self.test_sound_async
        )


    async def test_sound_async(self):

        self.status.value = (
            "🔊 TESTING WHISTLE"
        )

        self.page.update()


        await self.play_whistle()


        self.status.value = (
            f"{self.difficulty} • READY"
        )

        self.page.update()


    # =====================================================
    # GIVE CUE
    # =====================================================

    async def give_cue(self):

        if not self.running:

            return


        available_moves = [

            move

            for move in MOVES

            if move[0] != self.last_move

        ]


        move_name, sound_file = (
            random.choice(
                available_moves
            )
        )


        self.last_move = move_name


        self.move_label.value = (
            "MOVE NOW"
        )


        self.move_display.value = (
            move_name.upper()
        )


        self.move_display.color = (
            RED_LIGHT
        )


        self.page.update()


        await self.play_move_sound(
            move_name
        )


    # =====================================================
    # TRAINING LOOP
    # =====================================================

    async def session_loop(
        self,
        session_id,
    ):

        # -------------------------------------------------
        # COUNTDOWN
        # 0.5 second between numbers
        # -------------------------------------------------

        for number in [3, 2, 1]:

            if not self.running:

                return


            if session_id != self.session_id:

                return


            self.status.value = (
                f"{self.difficulty} • GET READY"
            )


            self.move_label.value = (
                "STARTING IN"
            )


            self.move_display.value = (
                str(number)
            )


            self.move_display.color = (
                WHITE
            )


            self.page.update()


            await asyncio.sleep(
                0.7
            )


        # -------------------------------------------------
        # START
        # -------------------------------------------------

        if not self.running:

            return


        if session_id != self.session_id:

            return


        self.status.value = (
            f"{self.difficulty} • TRAINING"
        )


        self.move_label.value = (
            "GO!"
        )


        self.move_display.value = (
            "🥊"
        )


        self.move_display.color = (
            RED_LIGHT
        )


        self.page.update()


        # START WHISTLE

        await self.play_whistle()

       # فاصل 0.7 ثانية بعد الصفارة
        await asyncio.sleep(0.7)

        if not self.running:
            return

        # START TIMER

        self.end_time = (
            time.monotonic()
            + self.duration
        )

        # FIRST MOVE

        await self.give_cue()  


        # =============================================
        # DIFFICULTY SPEED
        # =============================================

        min_delay, max_delay = (
            DIFFICULTIES[
                self.difficulty
            ]
        )


        # =============================================
        # MAIN TRAINING LOOP
        # =============================================

        while self.running:


            if session_id != self.session_id:

                return


            remaining = (
                self.end_time
                - time.monotonic()
            )


            if remaining <= 0:

                break


            self.timer_text.value = (
                self.format_time(
                    remaining
                )
            )


            elapsed = (
                self.duration
                - remaining
            )


            self.progress.value = max(

                0,

                min(

                    1,

                    elapsed
                    / self.duration,
                ),
            )


            self.page.update()


            # =========================================
            # RANDOM DELAY
            # =========================================

            delay = random.uniform(
                min_delay,
                max_delay,
            )


            target = (
                time.monotonic()
                + delay
            )


            # =========================================
            # WAIT
            # =========================================

            while (

                self.running

                and

                time.monotonic()
                < target

            ):


                if (
                    session_id
                    != self.session_id
                ):

                    return


                remaining = (
                    self.end_time
                    - time.monotonic()
                )


                if remaining <= 0:

                    break


                self.timer_text.value = (
                    self.format_time(
                        remaining
                    )
                )


                elapsed = (
                    self.duration
                    - remaining
                )


                self.progress.value = max(

                    0,

                    min(

                        1,

                        elapsed
                        / self.duration,
                    ),
                )


                self.page.update()


                await asyncio.sleep(
                    0.05
                )


            if not self.running:

                return


            if (
                time.monotonic()
                >= self.end_time
            ):

                break


            # =========================================
            # NEXT MOVE
            # =========================================

            await self.give_cue()


        # =================================================
        # FINISH
        # =================================================

        if session_id != self.session_id:

            return


        self.running = False


        self.status.value = (
            "SESSION FINISHED"
        )


        self.move_label.value = (
            "FINISHED"
        )


        self.move_display.value = (
            "🥊"
        )


        self.move_display.color = (
            RED_LIGHT
        )


        self.timer_text.value = (
            "00:00"
        )


        self.progress.value = 1


        self.start_btn.disabled = False

        self.stop_btn.disabled = True


        for button in self.duration_buttons:

            button.disabled = False


        for button in self.difficulty_buttons:

            button.disabled = False


        self.page.update()


        # =============================================
        # FINISH WHISTLE
        # =============================================

        self.page.run_task(
            self.play_whistle
        )


    # =====================================================
    # START SESSION
    # =====================================================

    def start_session(self, e):

        if self.running:

            return


        self.running = True


        self.session_id += 1


        current_session = (
            self.session_id
        )


        self.last_move = ""


        self.start_btn.disabled = True

        self.stop_btn.disabled = False


        for button in self.duration_buttons:

            button.disabled = True


        for button in self.difficulty_buttons:

            button.disabled = True


        self.status.value = (
            f"{self.difficulty} • GET READY"
        )


        self.move_label.value = (
            "STARTING IN"
        )


        self.move_display.value = (
            "3"
        )


        self.move_display.color = (
            WHITE
        )


        self.timer_text.value = (
            self.format_time(
                self.duration
            )
        )


        self.progress.value = 0


        self.page.update()


        self.page.run_task(

            self.session_loop,

            current_session,
        )


    # =====================================================
    # STOP SESSION
    # =====================================================

    def stop_session(self, e=None):

        if not self.running:

            return


        self.session_id += 1


        self.running = False


        self.start_btn.disabled = False

        self.stop_btn.disabled = True


        for button in self.duration_buttons:

            button.disabled = False


        for button in self.difficulty_buttons:

            button.disabled = False


        self.status.value = (
            "SESSION STOPPED"
        )


        self.move_label.value = (
            "READY"
        )


        self.move_display.value = (
            "READY"
        )


        self.move_display.color = (
            RED_LIGHT
        )


        self.timer_text.value = (
            self.format_time(
                self.duration
            )
        )


        self.progress.value = 0


        self.page.update()


# =========================================================
# MAIN
# =========================================================

def main(page: ft.Page):

    ReactionTrainer(page)


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    ft.run(
        main,
        assets_dir="assets",
    )