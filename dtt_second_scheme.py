from manim import *
from collections import namedtuple
import random

UserSet = namedtuple('UserSet', ['id', 'users'])

class DynamicConvergenceSchemeBinarySearch(Scene):
    def __init__(self, **kwargs):
         super().__init__(**kwargs)
         self.no_of_users = 16
         self.no_of_traitors = 3

    def construct(self):
        # Title
        title = Text("Dynamic Convergence Scheme: Second Method", font_size=36).to_edge(UP)
        self.play(Write(title))

        # Initialize The Center
        center = Rectangle(height=3, width=3, color=BLUE).next_to(title, DOWN, buff=1).to_edge(LEFT, buff=1)
        center_label = Text("The Center", font_size=36).move_to(center.get_center())
        self.play(Create(center), Write(center_label))
        self.wait(1)

        # Initialize users as nodes
        users_circles = VGroup(*[Circle(radius=0.25).set_color(GREEN) for _ in range(self.no_of_users)])
        user_labels = VGroup(*[Text(f"U{i+1}", font_size=16).move_to(user.get_center()) for i, user in enumerate(users_circles)])
        all_users = VGroup(*[VGroup(circle, label) for circle, label in zip(users_circles, user_labels)])
        all_users.arrange_in_grid(cols=2, buff=0.1).next_to(title, DOWN, buff=0.3).to_edge(RIGHT, buff=1)
        
        # choose traitors
        tratiors = random.sample(list(all_users), self.no_of_traitors)
        for traitor in tratiors:
            traitor[0].set_color(RED)

        innocent_users = VGroup(*[user for user in all_users])
        all_sets = [UserSet(0, innocent_users)] # THIS IS THE NON EMPTY SETS
        li_ri_rects = VGroup()

        innocent_rectangle = SurroundingRectangle(innocent_users, color=TEAL, buff=0.2)
        innocent_rectangle_label = Text("I", font_size=24).next_to(innocent_rectangle, RIGHT, buff=0.3)

        disconnected_users = VGroup()

        self.play(Create(users_circles), Create(innocent_rectangle), Write(user_labels), Write(innocent_rectangle_label))
        self.wait(1)

        # init t=0
        current_known_traitors = 0

        iteration_no = 0
        while len(tratiors) > 0:
            iteration_no += 1
            # for set in no_of_sets create variant
            variants = [Text(f"v{i}", font_size=24, color=YELLOW) for i in range(1, len(all_sets) + 1)]

            variant_set_map = dict()

            created_variants = VGroup()

            # Assign variants to sets
            for variant, user_set in zip(variants, all_sets):
                # animate variant moving from center to the relevant set
                variant_set_map[variant] = user_set
                current_variant = variant.copy().next_to(center.get_right(), RIGHT)
                created_variants.add(current_variant)
                if user_set.id == 0:
                    self.play(current_variant.animate.move_to(innocent_rectangle.get_left() + LEFT * 0.2), run_time=0.5)
                else:
                    print(all_sets)
                    print(li_ri_rects)
                    print(user_set.id)
                    self.play(current_variant.animate.move_to(li_ri_rects[user_set.id - 1].get_top() + RIGHT * 0.2), run_time=0.5)
            
            # Now I assigned all of those variants, time for the pirate to choose the traitor and broadcast
            chosen_traitor = random.choice(tratiors)
            self.play(Succession(*[Indicate(chosen_traitor) for _ in range(5)]), run_time=1.5)

            pirate_variant = None
            for variant in variant_set_map:
                if chosen_traitor in variant_set_map[variant].users:
                    pirate_variant = variant
                    # THEN this is the variant re-broadcasted py the pirate. cool.
            pirate_set = variant_set_map[pirate_variant]

            if pirate_set.id == 0: # Innocent set
                current_known_traitors += 1
                no_of_users_to_split = len(pirate_set.users)
                ### CREATION OF NEW LiRi, REQUIRES ME TO BE AWARE OF THE POSITIONS OF OTHER LiRis
                L_i_rect = Rectangle(color=PURE_BLUE, height=2.5, width=1.5)
                L_i = UserSet((current_known_traitors * 2) - 1, 
                              pirate_set.users[:no_of_users_to_split // 2])
                
                R_i_rect = Rectangle(color=PURE_RED, height=2.5, width=1.5)                              
                R_i = UserSet((current_known_traitors * 2), 
                              pirate_set.users[no_of_users_to_split // 2:])
                
                innocent_users.remove(*innocent_users)
                all_sets.pop(0) # remove innocent users
                all_sets.append(L_i)
                all_sets.append(R_i)
                # Animate the splitting to 2 new sets
                li_ri_rects.add(L_i_rect)
                li_ri_rects.add(R_i_rect)
                positioned_li_ri_rects = self._position_li_ri_rects(center, li_ri_rects)
                self.play(Transform(li_ri_rects, positioned_li_ri_rects))
                self.play(L_i.users.animate.arrange_in_grid(cols=2, buff=0.1).move_to(L_i_rect))
                self.play(R_i.users.animate.arrange_in_grid(cols=2, buff=0.1).move_to(R_i_rect))
                
            else:
                twin_set = self._find_twin_set(all_sets, pirate_set.id)

                # Move twin set users to I
                ### MOVE TWIN's USERS TO I
                innocent_users.add(*twin_set.users) #
                if not self._is_innocent_set_in_list(all_sets):
                    all_sets.insert(0, UserSet(0, innocent_users))
                twin_set.users.remove(*twin_set.users)
                self.play(innocent_users.animate.arrange_in_grid(cols=2, buff=0.1).move_to(innocent_rectangle))

                if len(pirate_set.users) == 1:
                    ###  DISCONNET THIS USER NOW
                    current_known_traitors -= 1
                    bad_user = pirate_set.users[0]
                    tratiors.remove(bad_user)
                    disconnected_users.add(bad_user)
                    self.play(bad_user.animate.move_to(ORIGIN))
                    cross = Cross().move_to(bad_user.get_center()).scale(0.4)
                    self.play(Create(cross))
                    self.play(Uncreate(bad_user), Uncreate(cross))
                    self.wait(0.5)
                    # REMOVE PIRATE AND TWIN SET FROM ALL_SETS
                    all_sets.remove(pirate_set)
                    all_sets.remove(twin_set)

                    # CREATE ALL_SETS FROM SCRATCH WITH RENUMBERED IDs
                    removed_rects = li_ri_rects[-2:]
                    li_ri_rects.remove(*li_ri_rects[-2:])
                    if len(li_ri_rects):
                        positioned_li_ri_rects = self._position_li_ri_rects(center, li_ri_rects)

                    reconstruct_animations = []
                    reconstructed_all_sets = []
                    for idx, user_set in enumerate(all_sets):
                        new_user_set = UserSet(idx, user_set.users)
                        reconstructed_all_sets.append(new_user_set)
                        if idx != 0:
                            reconstruct_animations.append(new_user_set.users.animate.arrange_in_grid(cols=2, buff=0.1).move_to(li_ri_rects[new_user_set.id - 1]))

                    all_sets = reconstructed_all_sets

                    if len(li_ri_rects):
                        self.play(Uncreate(removed_rects), Transform(li_ri_rects, positioned_li_ri_rects), *reconstruct_animations)

                else: # more than one user in the set
                    # SPLIT PIRATE SET INTO TWO PARTS
                    temp_vgroup = VGroup()
                    temp_vgroup.add(*pirate_set.users)
                    pirate_set.users.remove(*pirate_set.users)
                    pirate_set.users.add(*temp_vgroup[:len(temp_vgroup) // 2])
                    twin_set.users.add(*temp_vgroup[len(temp_vgroup) // 2:])

                    self.play(pirate_set.users.animate.arrange_in_grid(cols=2, buff=0.1).move_to(li_ri_rects[pirate_set.id - 1]),
                              twin_set.users.animate.arrange_in_grid(cols=2, buff=0.1).move_to(li_ri_rects[twin_set.id - 1]))
                
            test = Text(f"finished iteration number {iteration_no}", font_size=24)
            self.play(Write(test), run_time=0.7)
            self.wait(0.3)
            self.play(Unwrite(test), Uncreate(created_variants), run_time=0.7)

        self.wait(2)

    def _position_li_ri_rects(self, center_rect, li_ri_vgroup):
        positioned_vgroup = li_ri_vgroup.copy()
        positioned_vgroup[0].next_to(center_rect.get_bottom(), DOWN, buff=0.5).to_edge(LEFT)
        prev_rect = positioned_vgroup[0]
        for rect in positioned_vgroup[1:]:
            rect.next_to(prev_rect.get_right(), RIGHT, buff=0.1)
            prev_rect = rect
        return positioned_vgroup

    def _find_twin_set(self, set_list, set_id):
        wanted_id = set_id - 1 if set_id % 2 == 0 else set_id + 1
        for s in set_list:
            if s.id == wanted_id:
                return s
            
    def _is_innocent_set_in_list(self, set_list):
        for s in set_list:
            if s.id == 0: # Found innocent set
                return True
        return False

if __name__ == '__main__':
    config.quality = 'high_quality'
    scene = DynamicConvergenceSchemeBinarySearch()
    scene.render()