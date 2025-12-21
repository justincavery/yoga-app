-- Populate pose instructions for poses 41-60
-- This script adds detailed entry/exit instructions, holding cues, breathing patterns, and side variation flags
-- Run after applying the add_pose_instruction_fields migration

-- Batch 3: Poses 41-60

-- Pose 41: Wide-Legged Forward Bend (Prasarita Padottanasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Stand with your feet wide apart, about 4-5 feet, with your toes pointing forward or slightly in.',
    'Place your hands on your hips and inhale to lift your chest.',
    'Exhale as you hinge forward from your hips, keeping your spine long.',
    'Place your hands on the floor under your shoulders, or hold opposite elbows.',
    'Let your head hang or rest the crown of your head on the floor if it reaches.',
    'Keep your legs active and press through the outer edges of your feet.'
  ],
  exit_instructions = ARRAY[
    'Bring your hands back to your hips.',
    'Inhale and rise up slowly with a flat back, engaging your core.',
    'Exhale and step your feet together, returning to Mountain Pose.'
  ],
  holding_cues = 'Keep your weight forward in your feet, not back in your heels. Engage your leg muscles and lengthen your spine. Let gravity deepen the fold naturally.',
  breathing_pattern = 'Breathe deeply and evenly, holding for 5-10 breaths.',
  has_side_variation = false
WHERE name_english = 'Wide-Legged Forward Bend';

-- Pose 42: Gate Pose (Parighasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Begin kneeling with your knees hip-width apart.',
    'Extend your right leg straight out to the side with your foot flat on the floor.',
    'Inhale and extend your arms out to the sides at shoulder height.',
    'Exhale as you reach your right arm down toward your right leg and extend your left arm up and over your head.',
    'Create a gentle side bend, keeping both hips facing forward.',
    'Gaze up at your left hand or straight ahead.'
  ],
  exit_instructions = ARRAY[
    'Inhale and bring your torso back to center.',
    'Exhale and bring your right knee back to meet your left.',
    'Prepare to repeat on the opposite side.'
  ],
  holding_cues = 'Keep your hips facing forward and both sit bones even. Lengthen through both sides of your waist. Breathe into the stretched side.',
  breathing_pattern = 'Breathe deeply and evenly, holding for 5-8 breaths.',
  has_side_variation = true
WHERE name_english = 'Gate Pose';

-- Pose 43: Knees to Chest Pose (Apanasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Lie on your back with your knees bent and feet flat on the floor.',
    'Exhale as you draw both knees toward your chest.',
    'Wrap your arms around your shins or hold behind your thighs.',
    'Gently hug your knees closer to your chest.',
    'Keep your shoulders and head relaxed on the floor.',
    'Rock gently side to side if that feels good, massaging your back.'
  ],
  exit_instructions = ARRAY[
    'Release your knees and place your feet back on the floor.',
    'Extend your legs one at a time or both together.',
    'Rest briefly before moving into your next pose.'
  ],
  holding_cues = 'Keep your lower back pressing into the floor. Relax your shoulders and breathe into your belly. Let the pose gently massage your internal organs.',
  breathing_pattern = 'Breathe slowly and deeply, holding for 30-60 seconds.',
  has_side_variation = false
WHERE name_english = 'Knees to Chest Pose';

-- Pose 44: Reclining Hand to Big Toe Pose (Supta Padangusthasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Lie on your back with both legs extended.',
    'Bend your right knee and draw it toward your chest.',
    'Loop a strap around the ball of your right foot or hold your big toe with your first two fingers.',
    'Inhale and extend your right leg toward the ceiling, straightening it as much as possible.',
    'Keep your left leg active and pressing into the floor.',
    'Hold the strap with both hands or extend your left arm out to the side.'
  ],
  exit_instructions = ARRAY[
    'Bend your right knee and remove the strap.',
    'Exhale and lower your right leg back to the floor.',
    'Prepare to repeat on the opposite side.'
  ],
  holding_cues = 'Keep both hips grounded and your lower back on the floor. Keep your extended leg active. Breathe into the stretch in your hamstring.',
  breathing_pattern = 'Breathe deeply and evenly, holding for 30-60 seconds on each side.',
  has_side_variation = true
WHERE name_english = 'Reclining Hand to Big Toe Pose';

-- Pose 45: Low Lunge (Anjaneyasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'From Downward Facing Dog, step your right foot forward between your hands.',
    'Lower your left knee to the floor and release the top of your left foot.',
    'Inhale and sweep your arms overhead, bringing your palms together or keeping them shoulder-width apart.',
    'Exhale and sink your hips forward and down, keeping your right knee over your ankle.',
    'Lift through your chest and gently arch your back.',
    'Gaze forward or up toward your hands.'
  ],
  exit_instructions = ARRAY[
    'Exhale and lower your hands to frame your front foot.',
    'Tuck your back toes and step back to Downward Facing Dog.',
    'Prepare to repeat on the opposite side.'
  ],
  holding_cues = 'Keep your front knee at 90 degrees and your hips sinking low. Engage your core to protect your lower back. Lift through your chest.',
  breathing_pattern = 'Breathe deeply and evenly, holding for 5-8 breaths.',
  has_side_variation = true
WHERE name_english = 'Low Lunge';

-- Pose 46: Revolved Triangle Pose (Parivrtta Trikonasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'From standing, step your right foot forward about 3 feet, keeping your feet hip-width apart for balance.',
    'Square your hips to face forward.',
    'Inhale and extend your arms out to the sides.',
    'Exhale as you hinge forward and twist, bringing your left hand to the outside of your right foot or a block.',
    'Extend your right arm toward the ceiling, stacking your shoulders.',
    'Gaze up at your right hand or down at your left if balance is challenging.'
  ],
  exit_instructions = ARRAY[
    'Lower your top arm and bring both hands to your hips.',
    'Inhale and rise up to standing with a flat back.',
    'Step your feet together and prepare to repeat on the opposite side.'
  ],
  holding_cues = 'Keep both legs straight and active. Twist from your core, not just your shoulders. Use a block if needed to maintain length in your spine.',
  breathing_pattern = 'Breathe deeply and evenly, holding for 5-8 breaths.',
  has_side_variation = true
WHERE name_english = 'Revolved Triangle Pose';

-- Pose 47: Half Moon Pose (Ardha Chandrasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'From Triangle Pose on your right side, bend your right knee.',
    'Place your right hand on the floor or a block about 12 inches in front of your right foot.',
    'Shift your weight onto your right foot as you lift your left leg to hip height.',
    'Straighten your right leg and extend your left arm toward the ceiling.',
    'Stack your hips and shoulders, opening your chest.',
    'Gaze up at your top hand, forward, or down, depending on your balance.'
  ],
  exit_instructions = ARRAY[
    'Lower your top arm to your hip.',
    'Exhale and lower your left leg back to Triangle Pose.',
    'Step your feet together and prepare to repeat on the opposite side.'
  ],
  holding_cues = 'Keep your standing leg strong and your lifted leg active. Stack your hips and press through your raised heel. Engage your core for balance.',
  breathing_pattern = 'Breathe steadily to maintain balance, holding for 5-8 breaths.',
  has_side_variation = true
WHERE name_english = 'Half Moon Pose';

-- Pose 48: Warrior III (Virabhadrasana III)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Begin in Warrior I with your right foot forward.',
    'Shift your weight onto your right foot and engage your core.',
    'Inhale and begin to hinge forward, lifting your left leg behind you.',
    'Extend your arms forward or place your hands on your hips.',
    'Continue to hinge until your torso and left leg are parallel to the floor.',
    'Create one straight line from your fingertips to your left heel.',
    'Gaze down at the floor to keep your neck neutral.'
  ],
  exit_instructions = ARRAY[
    'Exhale and lower your back leg as you rise back to standing.',
    'Step your feet together and return to Mountain Pose.',
    'Prepare to repeat on the opposite side.'
  ],
  holding_cues = 'Keep your hips level and squared forward. Engage your core strongly and keep your standing leg active. Press through your raised heel.',
  breathing_pattern = 'Breathe steadily to maintain balance, holding for 5-8 breaths.',
  has_side_variation = true
WHERE name_english = 'Warrior III';

-- Pose 49: Revolved Side Angle Pose (Parivrtta Parsvakonasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'From a lunge with your right foot forward, bring your hands to prayer position at your heart.',
    'Inhale to lengthen your spine.',
    'Exhale and twist to the right, hooking your left elbow outside your right knee.',
    'Press your palms firmly together and use the resistance to deepen the twist.',
    'Keep your back leg straight and strong, or lower your back knee for more support.',
    'Gaze up toward the ceiling or straight ahead.'
  ],
  exit_instructions = ARRAY[
    'Release your hands to frame your front foot.',
    'Inhale and untwist, returning to center.',
    'Step back to Downward Facing Dog and prepare to repeat on the opposite side.'
  ],
  holding_cues = 'Keep your front knee at 90 degrees and your chest lifting. Twist from your core, keeping your spine long. Press your elbow against your knee for leverage.',
  breathing_pattern = 'Breathe deeply and evenly, holding for 5-8 breaths.',
  has_side_variation = true
WHERE name_english = 'Revolved Side Angle Pose';

-- Pose 50: Standing Split (Urdhva Prasarita Eka Padasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'From Standing Forward Bend, shift your weight onto your right foot.',
    'Inhale and lift your left leg behind you as high as you can.',
    'Place your hands on the floor, blocks, or hold your standing ankle.',
    'Keep your hips level and squared toward the floor.',
    'Engage your standing leg and press through your raised heel.',
    'Fold deeper over your standing leg, bringing your torso closer to your thigh.'
  ],
  exit_instructions = ARRAY[
    'Exhale and slowly lower your raised leg back to the floor.',
    'Return to Standing Forward Bend.',
    'Prepare to repeat on the opposite side.'
  ],
  holding_cues = 'Keep your hips squared toward the floor, not open to the side. Engage both legs actively. Fold from your hips, not your lower back.',
  breathing_pattern = 'Breathe deeply and evenly, holding for 5-8 breaths.',
  has_side_variation = true
WHERE name_english = 'Standing Split';

-- Pose 51: Eagle Pose (Garudasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Begin in Mountain Pose and shift your weight onto your left foot.',
    'Bend your knees slightly and cross your right thigh over your left.',
    'Hook your right foot behind your left calf if possible, or keep your toes on the floor.',
    'Extend your arms forward and cross your left arm over your right.',
    'Bend your elbows and bring your palms together, or press the backs of your hands together.',
    'Lift your elbows to shoulder height and sink your hips low.'
  ],
  exit_instructions = ARRAY[
    'Unwrap your arms and legs.',
    'Return to Mountain Pose and shake out your limbs.',
    'Prepare to repeat on the opposite side.'
  ],
  holding_cues = 'Sink your hips low and lift your elbows high. Keep your standing leg engaged. Find a focal point to help with balance.',
  breathing_pattern = 'Breathe steadily to maintain balance, holding for 5-8 breaths.',
  has_side_variation = true
WHERE name_english = 'Eagle Pose';

-- Pose 52: Bow Pose (Dhanurasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Lie on your belly with your arms alongside your body.',
    'Bend your knees and reach back to grasp your ankles with your hands.',
    'Inhale and simultaneously lift your chest and kick your feet into your hands.',
    'Lift your thighs off the floor as you arch your back.',
    'Draw your shoulder blades toward each other and lift through your chest.',
    'Gaze forward or slightly up, keeping your neck in a comfortable position.'
  ],
  exit_instructions = ARRAY[
    'Exhale and slowly release your feet, lowering your chest and thighs to the mat.',
    'Turn your head to one side and rest your arms alongside your body.',
    'Take several breaths before moving on.'
  ],
  holding_cues = 'Kick your feet actively into your hands to deepen the backbend. Keep your knees hip-width apart. Breathe into your chest and upper back.',
  breathing_pattern = 'Breathe steadily, holding for 5-8 breaths.',
  has_side_variation = false
WHERE name_english = 'Bow Pose';

-- Pose 53: Lizard Pose (Utthan Pristhasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'From Downward Facing Dog, step your right foot forward to the outside of your right hand.',
    'Lower your back knee to the floor and release the top of your left foot.',
    'Walk your hands inside your right foot if your hips are open enough.',
    'Lower down onto your forearms if accessible, or stay on your hands.',
    'Keep your right knee tracking over your right ankle.',
    'Sink your hips low and breathe into the stretch in your right hip.'
  ],
  exit_instructions = ARRAY[
    'Press up onto your hands if you lowered to your forearms.',
    'Tuck your back toes and step back to Downward Facing Dog.',
    'Prepare to repeat on the opposite side.'
  ],
  holding_cues = 'Keep your front knee aligned over your ankle. Sink your hips low and breathe into your hip flexors and groin. Keep your spine long.',
  breathing_pattern = 'Breathe deeply and evenly, holding for 30-60 seconds.',
  has_side_variation = true
WHERE name_english = 'Lizard Pose';

-- Pose 54: Reverse Warrior (Viparita Virabhadrasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'From Warrior II with your right knee bent, inhale and reach your right arm up toward the ceiling.',
    'Exhale and lean back, reaching your right arm up and back.',
    'Rest your left hand lightly on your back leg.',
    'Keep your right knee bent at 90 degrees and tracking over your ankle.',
    'Lift through your right side body, creating a gentle backbend.',
    'Gaze up at your right hand or straight ahead.'
  ],
  exit_instructions = ARRAY[
    'Inhale and return to Warrior II.',
    'Exhale and straighten your front leg.',
    'Prepare to repeat on the opposite side or move into your next pose.'
  ],
  holding_cues = 'Keep your front knee stable at 90 degrees. Lift through your side body and avoid collapsing into the backbend. Keep your back leg strong.',
  breathing_pattern = 'Breathe deeply and evenly, holding for 5-8 breaths.',
  has_side_variation = true
WHERE name_english = 'Reverse Warrior';

-- Pose 55: Fish Pose (Matsyasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Lie on your back with your legs extended and arms alongside your body.',
    'Slide your hands, palms down, under your hips.',
    'Inhale and press through your forearms and elbows to lift your chest.',
    'Arch your back and gently release the crown of your head to the floor.',
    'Keep most of your weight in your forearms, not your head.',
    'Hold your legs active or bend your knees and place your feet flat on the floor.'
  ],
  exit_instructions = ARRAY[
    'Press through your forearms to lift your head.',
    'Exhale and slowly lower your back to the floor.',
    'Rest with your arms alongside your body for a few breaths.'
  ],
  holding_cues = 'Keep your chest lifting high and your throat open. Most weight should be in your forearms. Breathe deeply into your chest.',
  breathing_pattern = 'Breathe deeply and evenly, holding for 5-10 breaths.',
  has_side_variation = false
WHERE name_english = 'Fish Pose';

-- Pose 56: Seated Wide-Legged Forward Bend (Upavistha Konasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Sit on your mat with your legs extended wide apart in a V shape.',
    'Flex your feet and keep your legs active.',
    'Place your hands on the floor in front of you.',
    'Inhale to lengthen your spine.',
    'Exhale and walk your hands forward, hinging from your hips.',
    'Keep your spine long and chest open as you fold forward.'
  ],
  exit_instructions = ARRAY[
    'Walk your hands back toward your body.',
    'Inhale and slowly roll up to seated, lifting your head last.',
    'Bring your legs together and shake them out.'
  ],
  holding_cues = 'Keep your legs active and kneecaps pointing up. Lead with your chest, not your head. Breathe into your inner thighs and hamstrings.',
  breathing_pattern = 'Breathe deeply, using each exhale to release a little deeper.',
  has_side_variation = false
WHERE name_english = 'Seated Wide-Legged Forward Bend';

-- Pose 57: Lord of the Dance Pose Full Expression (Natarajasana Full)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Begin in Mountain Pose and shift your weight onto your right foot.',
    'Bend your left knee and reach back with both hands to grasp your left foot.',
    'Inhale and begin to kick your left foot into your hands, lifting your leg behind you.',
    'Hinge forward from your hips, creating a deep backbend.',
    'Keep your chest lifting and your gaze forward.',
    'Find balance by engaging your core and standing leg strongly.'
  ],
  exit_instructions = ARRAY[
    'Slowly release your left foot and lower it to the ground.',
    'Return to Mountain Pose and take several breaths.',
    'Prepare to repeat on the opposite side.'
  ],
  holding_cues = 'Kick actively into your hands while keeping your hips level. Engage your core and standing leg strongly. Lift through your chest.',
  breathing_pattern = 'Breathe steadily to maintain balance, holding for 5-8 breaths.',
  has_side_variation = true
WHERE name_english = 'Lord of the Dance Pose Full Expression';

-- Pose 58: Revolved Head to Knee Pose (Parivrtta Janu Sirsasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Sit with your right leg extended and your left knee bent, left foot against your right inner thigh.',
    'Inhale and extend your left arm up and over your head.',
    'Exhale and reach for your right foot with your left hand, creating a side bend.',
    'Rest your right forearm on the floor inside your right leg.',
    'Rotate your chest toward the ceiling.',
    'Gaze up toward the ceiling or at your extended arm.'
  ],
  exit_instructions = ARRAY[
    'Inhale and slowly rise back to center.',
    'Exhale and switch legs.',
    'Prepare to repeat on the opposite side.'
  ],
  holding_cues = 'Keep both sit bones grounded. Create length along your side body. Breathe into the stretched side of your ribcage.',
  breathing_pattern = 'Breathe deeply, feeling expansion along your side body.',
  has_side_variation = true
WHERE name_english = 'Revolved Head to Knee Pose';

-- Pose 59: Supported Shoulderstand (Salamba Sarvangasana Variation)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Lie on your back with a folded blanket under your shoulders.',
    'Bend your knees and place your feet flat on the floor.',
    'Press your arms into the floor and lift your hips, then your legs.',
    'Support your back with your hands, walking them up toward your shoulder blades.',
    'Straighten your legs toward the ceiling, creating a vertical line.',
    'Keep your weight on your shoulders and upper arms, never on your neck.'
  ],
  exit_instructions = ARRAY[
    'Bend your knees toward your forehead.',
    'Support your back with your hands and slowly roll down.',
    'Rest for several breaths before sitting up.'
  ],
  holding_cues = 'Keep your neck neutral and weight off your neck. Engage your core and legs. Press your elbows toward each other.',
  breathing_pattern = 'Breathe deeply and evenly, holding for 30 seconds to several minutes.',
  has_side_variation = false
WHERE name_english = 'Supported Shoulderstand';

-- Pose 60: Side Crow Pose (Parsva Bakasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Begin in a squat position with your feet together.',
    'Twist your torso to the right, bringing your left elbow to the outside of your right thigh.',
    'Place your hands flat on the floor to the right of your feet.',
    'Shift your weight into your hands and engage your core.',
    'Lean forward and lift your feet off the floor, stacking your hips over your hands.',
    'Gaze forward and breathe steadily.'
  ],
  exit_instructions = ARRAY[
    'Exhale and slowly lower your feet back to the floor.',
    'Return to a squat or sit down.',
    'Prepare to repeat on the opposite side.'
  ],
  holding_cues = 'Press firmly through your hands and engage your core strongly. Keep your gaze forward to maintain balance. Squeeze your legs together.',
  breathing_pattern = 'Breathe steadily, holding for 3-5 breaths.',
  has_side_variation = true
WHERE name_english = 'Side Crow Pose';
