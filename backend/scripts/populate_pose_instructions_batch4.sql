-- Populate pose instructions for poses 61-80
-- This script adds detailed entry/exit instructions, holding cues, breathing patterns, and side variation flags
-- Run after applying the add_pose_instruction_fields migration

-- Batch 4: Poses 61-80

-- Pose 61: Flying Pigeon Pose (Eka Pada Galavasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'From a standing position, cross your right ankle over your left thigh in a figure-four position.',
    'Bend your standing leg and place your hands on the floor in front of you.',
    'Hook your right foot onto your left upper arm.',
    'Shift your weight forward into your hands, bending your elbows.',
    'Lift your left foot off the floor and extend your left leg straight back.',
    'Gaze forward and engage your core strongly.'
  ],
  exit_instructions = ARRAY[
    'Lower your left foot back to the floor.',
    'Release your right foot and return to standing.',
    'Prepare to repeat on the opposite side.'
  ],
  holding_cues = 'Press firmly through your hands and engage your core. Keep your elbows in and your gaze forward. Squeeze your hooked leg onto your arm.',
  breathing_pattern = 'Breathe steadily, holding for 3-5 breaths.',
  has_side_variation = true
WHERE name_english = 'Flying Pigeon Pose';

-- Pose 62: Scorpion Pose (Vrschikasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Begin in Forearm Stand with your legs extended straight up.',
    'Engage your core and begin to arch your back.',
    'Bend your knees and carefully lower your feet toward your head.',
    'Continue to arch your back, bringing your feet as close to your head as possible.',
    'Keep your weight balanced on your forearms.',
    'Gaze forward and breathe steadily.'
  ],
  exit_instructions = ARRAY[
    'Engage your core and slowly extend your legs back to Forearm Stand.',
    'Lower your legs with control to Dolphin Pose or Child''s Pose.',
    'Rest for several breaths before moving on.'
  ],
  holding_cues = 'Press firmly through your forearms and keep your shoulders stable. Engage your core to control the backbend. Breathe deeply into your chest.',
  breathing_pattern = 'Breathe slowly and deeply, holding for 3-5 breaths as you build strength.',
  has_side_variation = false
WHERE name_english = 'Scorpion Pose';

-- Pose 63: Peacock Pose (Mayurasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Kneel on the floor and bring your knees wide apart.',
    'Place your hands on the floor with fingers pointing back toward your feet.',
    'Bend your elbows and bring them together, resting your elbows on your abdomen.',
    'Lean forward and extend your legs straight back.',
    'Shift your weight forward and lift your feet and head off the floor.',
    'Create one straight line parallel to the floor.'
  ],
  exit_instructions = ARRAY[
    'Lower your feet and head back to the floor.',
    'Release the pose and sit back on your heels.',
    'Shake out your wrists and rest in Child''s Pose.'
  ],
  holding_cues = 'Press your elbows firmly into your abdomen. Engage your core and keep your body in one straight line. Gaze forward.',
  breathing_pattern = 'Breathe steadily, holding for 3-5 breaths.',
  has_side_variation = false
WHERE name_english = 'Peacock Pose';

-- Pose 64: Eight Angle Pose (Astavakrasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Sit with your legs extended in front of you.',
    'Bend your right knee and thread your right leg over your right shoulder.',
    'Cross your right ankle over your left ankle.',
    'Place your hands on the floor beside your hips.',
    'Shift your weight into your hands and lift your hips off the floor.',
    'Bend your elbows and lean to the right, extending both legs to the right side.',
    'Gaze forward and hold.'
  ],
  exit_instructions = ARRAY[
    'Straighten your arms and bring your hips back to center.',
    'Lower your hips to the floor and uncross your legs.',
    'Prepare to repeat on the opposite side.'
  ],
  holding_cues = 'Press firmly through your hands and engage your core. Keep your legs straight and squeezed together. Lean confidently to the side.',
  breathing_pattern = 'Breathe steadily, holding for 3-5 breaths.',
  has_side_variation = true
WHERE name_english = 'Eight Angle Pose';

-- Pose 65: Handstand (Adho Mukha Vrksasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Begin in Downward Facing Dog facing a wall for support.',
    'Walk your hands closer to the wall, about 6 inches away.',
    'Lift one leg high behind you.',
    'Inhale and hop or kick up, bringing both legs to the wall.',
    'Engage your core and press firmly through your hands.',
    'Stack your hips over your shoulders and extend your legs straight up.'
  ],
  exit_instructions = ARRAY[
    'Lower one leg at a time with control.',
    'Return to Downward Facing Dog or Child''s Pose.',
    'Rest for several breaths before continuing.'
  ],
  holding_cues = 'Press firmly through your hands and spread your fingers wide. Engage your core and keep your body in one straight line. Gaze between your thumbs.',
  breathing_pattern = 'Breathe steadily, holding for 5-10 breaths as you build strength.',
  has_side_variation = false
WHERE name_english = 'Handstand';

-- Pose 66: Full Wheel Pose (Chakrasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Lie on your back with your knees bent and feet flat on the floor, hip-width apart.',
    'Place your hands by your ears with fingers pointing toward your shoulders.',
    'Press through your hands and feet to lift your hips.',
    'Come briefly onto the crown of your head, then press up to straighten your arms.',
    'Walk your feet closer to your hands if possible to deepen the backbend.',
    'Press your chest toward the wall behind you.'
  ],
  exit_instructions = ARRAY[
    'Tuck your chin and slowly bend your elbows.',
    'Lower down carefully, vertebra by vertebra.',
    'Hug your knees to your chest and rock gently side to side.'
  ],
  holding_cues = 'Press firmly through your hands and feet. Keep your elbows from splaying out. Engage your legs and lift through your chest and shoulders.',
  breathing_pattern = 'Breathe deeply and evenly, holding for 5-10 breaths.',
  has_side_variation = false
WHERE name_english = 'Full Wheel Pose';

-- Pose 67: Heron Pose (Krounchasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Sit with your left leg bent and your left foot beside your left hip.',
    'Bend your right knee and clasp your right foot with both hands.',
    'Inhale and begin to straighten your right leg, bringing it toward vertical.',
    'Keep your spine long and chest lifted.',
    'Hold your foot with both hands or use a strap if needed.',
    'Gaze forward and keep your shoulders relaxed.'
  ],
  exit_instructions = ARRAY[
    'Bend your right knee and release your foot.',
    'Extend both legs forward and shake them out.',
    'Prepare to repeat on the opposite side.'
  ],
  holding_cues = 'Keep your spine long and both sit bones grounded. Draw your leg toward your torso rather than rounding your back. Engage your core.',
  breathing_pattern = 'Breathe deeply and evenly, holding for 5-8 breaths.',
  has_side_variation = true
WHERE name_english = 'Heron Pose';

-- Pose 68: One-Legged King Pigeon Pose Full (Eka Pada Rajakapotasana Full)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'From Pigeon Pose with your right leg forward, bend your left knee.',
    'Reach back with your left hand to grasp your left foot.',
    'Inhale and lift your chest.',
    'Reach back with your right hand to also grasp your left foot.',
    'Draw your left foot toward your head, deepening the backbend.',
    'Let your head drop back to rest on your left foot if possible.'
  ],
  exit_instructions = ARRAY[
    'Release your left foot and extend it back.',
    'Return to a gentle Pigeon Pose and rest.',
    'Prepare to repeat on the opposite side.'
  ],
  holding_cues = 'Keep your hips level and press your front shin into the floor. Engage your core to support your lower back. Breathe into your chest and hip flexors.',
  breathing_pattern = 'Breathe deeply and evenly, holding for 5-8 breaths.',
  has_side_variation = true
WHERE name_english = 'One-Legged King Pigeon Pose Full';

-- Pose 69: Yogic Sleep Pose (Yoganidrasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Lie on your back and draw both knees toward your chest.',
    'Bring your right foot behind your head, resting it on your neck.',
    'Bring your left foot behind your head as well, crossing your ankles.',
    'Clasp your hands together in front of your chest or behind your back.',
    'Relax as much as possible into this deep forward fold.',
    'Breathe calmly despite the intensity of the pose.'
  ],
  exit_instructions = ARRAY[
    'Carefully release your feet one at a time.',
    'Hug your knees to your chest and rock gently.',
    'Rest in Corpse Pose for several breaths.'
  ],
  holding_cues = 'Relax your neck and allow your legs to rest on your shoulders. Breathe slowly and deeply. Stay calm and focused.',
  breathing_pattern = 'Breathe slowly and deeply, holding for 30-60 seconds.',
  has_side_variation = false
WHERE name_english = 'Yogic Sleep Pose';

-- Pose 70: Forearm Wheel Pose (Dwi Pada Viparita Dandasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Begin in Wheel Pose with your hands and feet on the floor.',
    'Walk your feet closer to your hands.',
    'Lower one forearm to the floor, then the other.',
    'Interlace your fingers or keep your forearms parallel.',
    'Press your chest even higher and arch your back deeply.',
    'Gaze back toward the floor behind you.'
  ],
  exit_instructions = ARRAY[
    'Place your hands back on the floor, one at a time.',
    'Return to Wheel Pose, then lower down carefully.',
    'Hug your knees to your chest and rest.'
  ],
  holding_cues = 'Press firmly through your forearms and feet. Keep your legs active and hips lifting. Breathe into your chest and upper back.',
  breathing_pattern = 'Breathe deeply and evenly, holding for 3-5 breaths.',
  has_side_variation = false
WHERE name_english = 'Forearm Wheel Pose';

-- Pose 71: Splits (Hanumanasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'From a low lunge with your right foot forward, place your hands on the floor on either side of your hips.',
    'Begin to slide your right foot forward and your left leg back.',
    'Keep your hips squared forward as you slowly lower down.',
    'Use blocks under your hands for support if needed.',
    'Continue to slide your legs apart until you reach your edge.',
    'Square your hips and lift through your chest.'
  ],
  exit_instructions = ARRAY[
    'Press through your hands to lift your hips slightly.',
    'Bend your front knee and slide back to a low lunge.',
    'Rest in Child''s Pose before repeating on the opposite side.'
  ],
  holding_cues = 'Keep your hips squared forward and your legs active. Use props to support yourself at your current level. Breathe into your hamstrings and hip flexors.',
  breathing_pattern = 'Breathe deeply and evenly, holding for 30-60 seconds.',
  has_side_variation = true
WHERE name_english = 'Splits';

-- Pose 72: Feathered Peacock Pose (Pincha Mayurasana Advanced)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Begin in Dolphin Pose with your forearms on the floor.',
    'Walk your feet as close to your elbows as possible.',
    'Lift one leg high behind you.',
    'Hop or float your bottom leg up to meet your top leg.',
    'Stack your hips over your shoulders and extend both legs straight up.',
    'Engage your core and press firmly through your forearms.'
  ],
  exit_instructions = ARRAY[
    'Lower your legs with control, one at a time.',
    'Return to Dolphin Pose or Child''s Pose.',
    'Rest for several breaths.'
  ],
  holding_cues = 'Press firmly through your forearms and engage your shoulders. Keep your core engaged and legs active. Gaze between your hands.',
  breathing_pattern = 'Breathe steadily, holding for 5-10 breaths.',
  has_side_variation = false
WHERE name_english = 'Feathered Peacock Pose';

-- Pose 73: Twisted Flying Crow (Eka Pada Koundinyasana I)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'From a lunge with your right foot forward, twist your torso to the right.',
    'Place your hands flat on the floor to the right of your front foot.',
    'Hook your left shoulder under your right thigh.',
    'Shift your weight into your hands and begin to lift both feet off the floor.',
    'Extend your right leg forward and your left leg back.',
    'Gaze forward and engage your core strongly.'
  ],
  exit_instructions = ARRAY[
    'Lower your feet back to the floor.',
    'Return to a lunge or step back to Downward Facing Dog.',
    'Prepare to repeat on the opposite side.'
  ],
  holding_cues = 'Press firmly through your hands and engage your core. Keep your shoulders stable and your gaze forward. Extend through both legs.',
  breathing_pattern = 'Breathe steadily, holding for 3-5 breaths.',
  has_side_variation = true
WHERE name_english = 'Twisted Flying Crow';

-- Pose 74: Upward Plank Pose (Purvottanasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Sit in Staff Pose with your legs extended in front of you.',
    'Place your hands behind you with fingers pointing toward your feet.',
    'Press through your hands and feet as you lift your hips toward the ceiling.',
    'Keep your legs straight and press through your heels.',
    'Let your head drop back gently if comfortable for your neck.',
    'Create one straight line from your heels to your shoulders.'
  ],
  exit_instructions = ARRAY[
    'Exhale and slowly lower your hips back to the floor.',
    'Return to Staff Pose or shake out your wrists.',
    'Rest before moving to your next pose.'
  ],
  holding_cues = 'Press firmly through your hands and feet. Engage your glutes and legs. Keep your chest lifting and avoid letting your hips sag.',
  breathing_pattern = 'Breathe deeply and evenly, holding for 5-8 breaths.',
  has_side_variation = false
WHERE name_english = 'Upward Plank Pose';

-- Pose 75: Noose Pose (Pasasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Begin in a deep squat with your feet together.',
    'Twist your torso to the right.',
    'Bring your left arm to the outside of your right thigh.',
    'Wrap your left arm around your legs and reach your right arm behind your back.',
    'Clasp your hands together behind your back if possible.',
    'Keep your heels on the floor or place a folded blanket under them.'
  ],
  exit_instructions = ARRAY[
    'Release your hands and untwist.',
    'Return to center and stand up or sit down.',
    'Prepare to repeat on the opposite side.'
  ],
  holding_cues = 'Keep your heels grounded and your knees together. Twist from your core and lengthen your spine. Breathe into your back body.',
  breathing_pattern = 'Breathe deeply and evenly, holding for 5-8 breaths.',
  has_side_variation = true
WHERE name_english = 'Noose Pose';

-- Pose 76: One-Handed Tiger Pose (Eka Hasta Bhujasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Sit with your legs extended in front of you.',
    'Bend your right knee and thread your right leg over your right shoulder.',
    'Place your hands on the floor beside your hips.',
    'Shift your weight into your hands and lift your hips off the floor.',
    'Extend your left leg forward, keeping it straight.',
    'Gaze forward and engage your core.'
  ],
  exit_instructions = ARRAY[
    'Lower your hips back to the floor.',
    'Release your right leg from your shoulder.',
    'Prepare to repeat on the opposite side.'
  ],
  holding_cues = 'Press firmly through your hands and engage your core. Keep your extended leg straight and active. Squeeze your bent leg onto your arm.',
  breathing_pattern = 'Breathe steadily, holding for 3-5 breaths.',
  has_side_variation = true
WHERE name_english = 'One-Handed Tiger Pose';

-- Pose 77: Tortoise Pose (Kurmasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Sit with your legs wide apart in front of you.',
    'Bend your knees and slide your arms under your knees.',
    'Extend your arms out to the sides, palms facing down.',
    'Begin to straighten your legs, pressing them onto your shoulders.',
    'Fold forward, bringing your chest and forehead toward the floor.',
    'Breathe into your back body and relax into the pose.'
  ],
  exit_instructions = ARRAY[
    'Bend your knees and slide your arms out from under your legs.',
    'Sit up slowly and extend your legs forward.',
    'Shake out your legs and rest.'
  ],
  holding_cues = 'Let your legs rest on your shoulders and your chest melt toward the floor. Breathe deeply into your back. Relax your neck and jaw.',
  breathing_pattern = 'Breathe slowly and deeply, holding for 30-60 seconds.',
  has_side_variation = false
WHERE name_english = 'Tortoise Pose';

-- Pose 78: Destroyer of the Universe Pose (Bhairavasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Begin in a standing position and shift your weight onto your right foot.',
    'Bend your left knee and grasp your left foot with your left hand.',
    'Extend your left leg out to the side while balancing on your right foot.',
    'Reach your right arm overhead or out to the side for balance.',
    'Keep your standing leg strong and your core engaged.',
    'Gaze forward to maintain balance.'
  ],
  exit_instructions = ARRAY[
    'Slowly release your left foot and lower it to the ground.',
    'Return to standing and shake out your legs.',
    'Prepare to repeat on the opposite side.'
  ],
  holding_cues = 'Keep your standing leg strong and your core engaged. Press your foot into your hand to extend your leg. Maintain steady breathing.',
  breathing_pattern = 'Breathe steadily to maintain balance, holding for 5-8 breaths.',
  has_side_variation = true
WHERE name_english = 'Destroyer of the Universe Pose';

-- Pose 79: Shoulder Pressing Pose (Bhujapidasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Stand with your feet hip-width apart and bend forward.',
    'Place your hands on the floor between your legs.',
    'Bend your knees and place them on the backs of your upper arms.',
    'Shift your weight into your hands and lift your feet off the floor.',
    'Cross your ankles if possible.',
    'Gaze forward and engage your core strongly.'
  ],
  exit_instructions = ARRAY[
    'Uncross your ankles and lower your feet to the floor.',
    'Stand up or sit down.',
    'Shake out your wrists and rest.'
  ],
  holding_cues = 'Press firmly through your hands and engage your core. Squeeze your knees onto your arms. Keep your gaze forward.',
  breathing_pattern = 'Breathe steadily, holding for 3-5 breaths.',
  has_side_variation = false
WHERE name_english = 'Shoulder Pressing Pose';

-- Pose 80: Formidable Face Pose (Gandha Bherundasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Lie on your belly with your hands by your shoulders.',
    'Press up into a very deep backbend, walking your hands toward your feet.',
    'Bend your elbows and rest your chin and chest on the floor.',
    'Lift your feet high, bringing them toward your head.',
    'Balance on your chin, chest, and forearms.',
    'Breathe calmly despite the intensity.'
  ],
  exit_instructions = ARRAY[
    'Carefully extend your arms to lift your chest.',
    'Lower your legs and return to lying on your belly.',
    'Rest in Child''s Pose for several breaths.'
  ],
  holding_cues = 'Keep your core engaged and your legs active. Balance your weight carefully between your chin, chest, and arms. Breathe steadily.',
  breathing_pattern = 'Breathe slowly and deeply, holding for 3-5 breaths.',
  has_side_variation = false
WHERE name_english = 'Formidable Face Pose';
