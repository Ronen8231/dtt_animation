from manim import *
import itertools
import random

class DynamicConvergenceScheme(Scene):
    def __init__(self, **kwargs):
         super().__init__(**kwargs)
         self.no_of_users = 8
         self.no_of_traitors = 3

    def construct(self):
        # Title
        title = Text("Dynamic Convergence Scheme: First Method", font_size=36).to_edge(UP)
        self.play(Write(title))

        # Initialize The Center
        center = Rectangle(height=3, width=3, color=BLUE).next_to(title, DOWN, buff=1).to_edge(LEFT, buff=1)
        center_label = Text("The Center", font_size=36).move_to(center.get_center())
        self.play(Create(center), Write(center_label))
        self.wait(1)

        # Initialize users as nodes
        users = VGroup(*[Circle(radius=0.4).set_color(GREEN) for _ in range(self.no_of_users)])
        users.arrange_in_grid(cols=2, buff=0.5).next_to(title, DOWN, buff=1).to_edge(RIGHT, buff=1)
        user_labels = VGroup(*[Text(f"U{i+1}", font_size=24).move_to(user.get_center()) for i, user in enumerate(users)])
        
        # choose traitors
        tratiors = random.sample(list(users), self.no_of_traitors)
        for traitor in tratiors:
            traitor.set_color(RED)

        self.play(Create(users), Write(user_labels))
        self.wait(1)

        # init t=0
        current_known_traitors = 0

        while len(tratiors) > 0:
            variants = [Text(f"v{i}", font_size=24, color=PURPLE) for i in range(1, current_known_traitors + 2)]
            expected_variants = variants[:-1]

            succssesful_tracing = False

            for combination in itertools.combinations(users, current_known_traitors):
                created_variants = VGroup()
                user_variant_map = dict()

                # assigning variants
                for idx, user in enumerate(combination):
                    current_variant = variants[idx].copy().set_color(YELLOW).next_to(center.get_right(), RIGHT)
                    created_variants.add(current_variant)
                    user_variant_map[user] = current_variant
                    # self.play(Create(current_variant), run_time=0.5)
                    self.play(current_variant.animate.move_to(user.get_top() + UP * 0.2), run_time=0.5)

                # assigning the last variant for remaining users
                remaining_users = [user for user in users if user not in combination]
                remaining_variants = [variants[-1].copy().next_to(center.get_right(), RIGHT) for _ in remaining_users]
                remaining_anims = []
                for user, current_variant in zip(remaining_users, remaining_variants):
                    created_variants.add(current_variant)
                    user_variant_map[user] = current_variant
                    remaining_anims.append(current_variant.animate.move_to(user.get_top() + UP * 0.2))
                self.play(*remaining_anims, run_time=0.5)

                # choose traitor to rebroadcast his variant
                chosen_traitor = random.choice(tratiors)
                self.play(Succession(*[Indicate(chosen_traitor) for _ in range(5)]), run_time=1.5)

                pirate_broadcasted_variant = user_variant_map[chosen_traitor]
                pirate_broadcast_text = Text(f"Pirate Broadcasted Variant {pirate_broadcasted_variant.original_text}", font_size=30).move_to(ORIGIN)
                self.play(Write(pirate_broadcast_text))
                self.wait(0.5)
                self.play(Unwrite(pirate_broadcast_text))
                
                # check if we successfuly traced the traitor
                for variant in expected_variants:
                    if variant.original_text == pirate_broadcasted_variant.original_text:
                        succssesful_tracing = True
                        pirate_tracing_text = Text(f"Successfully traced traitor!", font_size=30).move_to(ORIGIN)
                        cross = Cross().move_to(chosen_traitor.get_center()).scale(0.7)
                        self.play(Write(pirate_tracing_text), Create(cross))
                        self.wait(0.5)
                        self.play(Unwrite(pirate_tracing_text))
                        users.remove(chosen_traitor)
                        tratiors.remove(chosen_traitor)
                
                self.wait(0.5)
                self.play(Uncreate(created_variants))

                if succssesful_tracing:
                    break
                
                # if pirate broadcast is not the last variant, we found him!
                # eliminate this mfer - put a huge X on it and remove it from the list of the users
                # if we actually found him, we should probably start the while True
            
            if not succssesful_tracing:
                current_known_traitors += 1
            else:
                current_known_traitors -= 1

        self.wait(2)


if __name__ == '__main__':
    scene = DynamicConvergenceScheme()
    scene.render()