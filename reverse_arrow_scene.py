from manim import *
import numpy as np


class ReverseArrowLinear(Scene):
    @staticmethod
    def calc_result(n):
        return 3 if n <= 2 else 3 * (2 ** (n - 2))

    @staticmethod
    def format_result(value):
        return f"{value:.2e}" if value >= 10**6 else f"{value:,.0f}"

    def construct(self):
        self.camera.background_color = "#111827"
        title = Text("2 <- n 계산 결과", font_size=32, color=BLUE_B).to_edge(UP)
        self.play(FadeIn(title, shift=DOWN * 0.15), run_time=0.7)

        # 축의 외형은 고정하고 데이터 좌표를 연속적으로 변환한다.
        # 이미 그린 선과 점도 같은 축척을 사용하므로 확대/축소 때 어긋나지 않는다.
        axes = Axes(
            x_range=[0, 1, 0.1],
            y_range=[0, 1, 0.2],
            x_length=9,
            y_length=4.8,
            axis_config={"color": GREY_B, "stroke_width": 1.5},
            tips=False,
        ).shift(DOWN * 0.65)
        x_label = Text("n", font_size=20).next_to(axes.x_axis, RIGHT)
        y_label = Text("Result", font_size=20).next_to(axes.y_axis, UP)
        self.play(Create(axes), FadeIn(x_label), FadeIn(y_label), run_time=0.8)

        n_vals = np.arange(1, 50)
        results = np.array([self.calc_result(int(n)) for n in n_vals], dtype=float)
        x_limit = ValueTracker(10)
        y_limit = ValueTracker(self.calc_result(10) * 1.25)
        progress = ValueTracker(0)

        def point(n, value):
            return axes.c2p(n / x_limit.get_value(), value / y_limit.get_value())

        def visible_data():
            p = min(max(progress.get_value(), 0), len(n_vals) - 1)
            index = int(np.floor(p))
            values = list(zip(n_vals[: index + 1], results[: index + 1]))
            if index < len(n_vals) - 1:
                fraction = p - index
                values.append((
                    interpolate(n_vals[index], n_vals[index + 1], fraction),
                    interpolate(results[index], results[index + 1], fraction),
                ))
            return values

        def make_curve():
            points = [point(n, value) for n, value in visible_data()]
            if len(points) == 1:
                points.append(points[0])
            return VMobject(color=TEAL_A, stroke_width=3).set_points_as_corners(points)

        curve = always_redraw(make_curve)
        dots = always_redraw(lambda: VGroup(*[
            Dot(point(n, value), radius=0.035, color=TEAL_A)
            for n, value in visible_data()[:-1]
        ]))
        head = always_redraw(lambda: Dot(point(*visible_data()[-1]), radius=0.065, color=PINK))
        # 등간격 눈금마다 실제 값을 표시해 선형 축척을 읽을 수 있게 한다.
        y_ticks = always_redraw(lambda: VGroup(*[
            Text(self.format_result(y_limit.get_value() * fraction),
                 font_size=15, color=GREY_A)
            .next_to(axes.c2p(0, fraction), LEFT, buff=0.18)
            for fraction in (0.2, 0.4, 0.6, 0.8, 1.0)
        ]))
        x_ticks = always_redraw(lambda: VGroup(*[
            Text(f"{x_limit.get_value() * fraction:.0f}",
                 font_size=15, color=GREY_A)
            .next_to(axes.c2p(fraction, 0), DOWN, buff=0.15)
            for fraction in (0.2, 0.4, 0.6, 0.8, 1.0)
        ]))

        def readout(n, value):
            return Text(
                f"n = {n}    Result = {self.format_result(value)}",
                font_size=24, color=YELLOW,
            ).move_to(UP * 2.65)

        # 수치는 단계가 완료될 때만 교체하고 축 눈금은 축소할 때만 갱신한다.
        value_text = readout(1, results[0])
        self.add(curve, dots, head, y_ticks, x_ticks)
        self.play(FadeIn(value_text), run_time=0.4)
        self.wait(0.4)

        y_ticks.suspend_updating()
        x_ticks.suspend_updating()
        for index in range(1, len(n_vals)):
            n, value = int(n_vals[index]), results[index]
            # 몇 개의 점을 같은 선형 축척에서 그려 두 배씩 증가하는 모습을 보여준다.
            # 범위를 넘기 직전에만 기존 그래프 전체를 함께 축소한다.
            if value > y_limit.get_value() or n > x_limit.get_value():
                last_in_view = min(n + 3, int(n_vals[-1]))
                target_x = max(x_limit.get_value(), np.ceil(last_in_view / 5) * 5)
                target_y = self.calc_result(last_in_view) * 1.25
                self.wait(0.18)
                y_ticks.resume_updating()
                x_ticks.resume_updating()
                self.play(
                    x_limit.animate.set_value(target_x),
                    y_limit.animate.set_value(target_y),
                    run_time=0.85,
                    rate_func=smooth,
                )
                y_ticks.suspend_updating()
                x_ticks.suspend_updating()

            self.play(
                progress.animate.set_value(index),
                run_time=max(0.32, 0.5 - index * 0.003),
                rate_func=smooth,
            )
            value_text.become(readout(n, value))

        self.wait(2)
