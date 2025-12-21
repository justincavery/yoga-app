-- Populate pose instructions for poses 21-40
-- This script adds detailed entry/exit instructions, holding cues, breathing patterns, and side variation flags
-- Run after applying the add_pose_instruction_fields migration

-- Batch 2: Poses 21-40

-- Pose 21: Crow Pose (Bakasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Begin in a squat position with your feet together and hands planted on the mat shoulder-width apart.',
    'Spread your fingers wide and press firmly through your palms.',
    'Come onto the balls of your feet and bring your knees to rest on the backs of your upper arms.',
    'Inhale as you lean forward, shifting your weight into your hands.',
    'Exhale and begin to lift one foot at a time off the floor, bringing your heels toward your buttocks.',
    'Engage your core strongly and gaze forward, not down.'
  ],
  exit_instructions = ARRAY[
    'Exhale as you slowly lower your feet back to the floor.',
    'Come back to a squat position or step back to Child''s Pose.',
    'Rest for a few breaths before moving on.'
  ],
  holding_cues = 'Press firmly through your hands and engage your core. Draw your knees tightly into your arms. Keep your gaze forward to maintain balance.',
  breathing_pattern = 'Breathe steadily and evenly, holding for 3-5 breaths as you build strength.',
  has_side_variation = false
WHERE name_english = 'Crow Pose';

-- Pose 22: Headstand (Sirsasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Begin on your hands and knees, then lower your forearms to the floor with elbows shoulder-width apart.',
    'Interlace your fingers to create a basket with your hands.',
    'Place the crown of your head on the floor, cradling the back of your head with your hands.',
    'Tuck your toes and lift your hips, walking your feet closer to your elbows.',
    'When your hips are over your shoulders, engage your core and slowly lift one leg, then the other.',
    'Extend your legs straight up toward the ceiling, creating one straight line.'
  ],
  exit_instructions = ARRAY[
    'Engage your core and slowly lower your legs with control, one at a time or together.',
    'Lower your knees to the floor and rest in Child''s Pose for at least 1 minute.',
    'Allow your blood pressure to normalize before sitting up.'
  ],
  holding_cues = 'Press firmly through your forearms and engage your shoulders to support your weight. Keep your core engaged and your legs active. Breathe steadily and remain calm.',
  breathing_pattern = 'Breathe slowly and deeply, holding for 30 seconds to several minutes as your practice develops.',
  has_side_variation = false
WHERE name_english = 'Headstand';

-- Pose 23: Wheel Pose (Urdhva Dhanurasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Lie on your back with your knees bent and feet flat on the floor, hip-width apart.',
    'Place your hands by your ears with fingers pointing toward your shoulders.',
    'Inhale as you press through your hands and feet, lifting your hips off the floor.',
    'Come onto the crown of your head briefly, adjusting hand and foot position if needed.',
    'Exhale and press firmly through your hands to straighten your arms, lifting into a full backbend.',
    'Keep your feet parallel and press your chest toward the wall behind you.'
  ],
  exit_instructions = ARRAY[
    'Tuck your chin to your chest and slowly bend your elbows.',
    'Exhale as you lower down carefully, bringing your shoulders, then back, then hips to the floor.',
    'Hug your knees to your chest and rock gently side to side to release your lower back.'
  ],
  holding_cues = 'Press firmly through your hands and feet. Keep your elbows from splaying out and your knees from falling in. Engage your legs and lift through your chest.',
  breathing_pattern = 'Breathe deeply and evenly, holding for 3-5 breaths initially.',
  has_side_variation = false
WHERE name_english = 'Wheel Pose';

-- Pose 24: Side Plank (Vasisthasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Begin in Downward Facing Dog or Plank Pose.',
    'Shift your weight onto your right hand and the outer edge of your right foot.',
    'Inhale as you stack your left foot on top of your right and extend your left arm toward the ceiling.',
    'Lift your hips high and create one straight line from your head to your heels.',
    'Gaze up at your left hand, forward, or down, depending on your neck comfort.',
    'Engage your core and press firmly through your supporting hand.'
  ],
  exit_instructions = ARRAY[
    'Exhale as you lower your left hand to the floor.',
    'Return to Plank or Downward Facing Dog.',
    'Prepare to repeat on the opposite side.'
  ],
  holding_cues = 'Keep your body in one straight line without letting your hips sag. Press away from the floor through your supporting hand. Engage your core and legs strongly.',
  breathing_pattern = 'Breathe steadily for 5-8 breaths, maintaining strength and stability.',
  has_side_variation = true
WHERE name_english = 'Side Plank';

-- Pose 25: King Dancer Pose (Natarajasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Begin in Mountain Pose, shifting your weight onto your right foot.',
    'Bend your left knee and reach back with your left hand to grasp the inside of your left foot or ankle.',
    'Inhale as you extend your right arm forward and up, finding your balance.',
    'Exhale and begin to kick your left foot into your hand, lifting your leg behind you.',
    'Hinge forward slightly from your hips, keeping your spine long.',
    'Fix your gaze on a non-moving point to help maintain balance.'
  ],
  exit_instructions = ARRAY[
    'Slowly release your left foot and lower it to the ground.',
    'Return to Mountain Pose and take a few breaths.',
    'Prepare to repeat on the opposite side.'
  ],
  holding_cues = 'Keep your standing leg strong and your core engaged. Press your foot into your hand to deepen the backbend. Keep your hips level and squared forward.',
  breathing_pattern = 'Breathe slowly and evenly to maintain balance, holding for 5-8 breaths.',
  has_side_variation = true
WHERE name_english = 'King Dancer Pose';

-- Pose 26: Forearm Stand (Pincha Mayurasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Begin in Dolphin Pose with your forearms parallel and elbows shoulder-width apart.',
    'Walk your feet as close to your elbows as possible.',
    'Inhale and lift one leg high behind you.',
    'Exhale and hop or float your bottom leg up to meet your top leg.',
    'Stack your hips over your shoulders and extend both legs straight up.',
    'Engage your core strongly and gaze between your hands.'
  ],
  exit_instructions = ARRAY[
    'Lower your legs with control, one at a time.',
    'Return to Dolphin Pose or Child''s Pose.',
    'Rest for several breaths before continuing.'
  ],
  holding_cues = 'Press firmly through your forearms and engage your shoulders. Keep your core engaged and your legs active. Maintain steady breathing to stay balanced.',
  breathing_pattern = 'Breathe slowly and deeply, holding for 5-10 breaths as you build strength.',
  has_side_variation = false
WHERE name_english = 'Forearm Stand';

-- Pose 27: Firefly Pose (Tittibhasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Begin in a wide-legged squat with your feet wider than hip-width apart.',
    'Place your hands flat on the floor behind your feet, shoulder-width apart.',
    'Thread your shoulders under your knees, bringing your upper arms as far under your thighs as possible.',
    'Inhale to prepare, then exhale as you shift your weight into your hands.',
    'Engage your core and slowly lift your feet off the floor, straightening your legs as much as possible.',
    'Gaze forward and keep your chest lifted.'
  ],
  exit_instructions = ARRAY[
    'Exhale as you bend your knees and slowly lower your feet back to the floor.',
    'Return to a squat position or sit down.',
    'Rest and shake out your wrists before moving on.'
  ],
  holding_cues = 'Press firmly through your hands and engage your core strongly. Squeeze your thighs against your arms. Keep your gaze forward to maintain balance.',
  breathing_pattern = 'Breathe steadily, holding for 3-5 breaths as you build strength.',
  has_side_variation = false
WHERE name_english = 'Firefly Pose';

-- Pose 28: Bound Angle Pose (Baddha Konasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Sit on your mat with your legs extended in front of you.',
    'Bend your knees and bring the soles of your feet together, allowing your knees to fall out to the sides.',
    'Draw your heels as close to your pelvis as is comfortable.',
    'Grasp your feet or ankles with your hands.',
    'Inhale to lengthen your spine, sitting up tall.',
    'Exhale and either stay upright or fold forward from your hips, keeping your spine long.'
  ],
  exit_instructions = ARRAY[
    'Inhale and slowly rise back to an upright seated position if you folded forward.',
    'Release your feet and gently bring your knees together.',
    'Extend your legs forward and shake them out.'
  ],
  holding_cues = 'Keep your spine long and sit bones grounded. Let your knees release naturally toward the floor without forcing. Relax your hip flexors and breathe into your inner thighs.',
  breathing_pattern = 'Breathe deeply and evenly, allowing gravity to gently open your hips.',
  has_side_variation = false
WHERE name_english = 'Bound Angle Pose';

-- Pose 29: Plow Pose (Halasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Lie on your back with your arms alongside your body, palms facing down.',
    'Engage your core and press your arms into the floor as you lift your legs and hips.',
    'Inhale and bring your legs up and over your head, allowing your feet to come toward the floor behind you.',
    'Support your back with your hands if needed, or interlace your fingers on the floor.',
    'Exhale and relax your legs, allowing your toes to touch the floor if they reach.',
    'Keep your neck neutral and avoid turning your head.'
  ],
  exit_instructions = ARRAY[
    'Place your hands on your back for support if they aren''t already there.',
    'Exhale and slowly roll down, lowering your spine vertebra by vertebra.',
    'Rest with your knees bent or legs extended, breathing naturally.'
  ],
  holding_cues = 'Keep your shoulders grounded and avoid putting weight on your neck. Engage your core and legs. Breathe deeply into your back body.',
  breathing_pattern = 'Breathe slowly and deeply, holding for 5-10 breaths.',
  has_side_variation = false
WHERE name_english = 'Plow Pose';

-- Pose 30: Shoulder Stand (Sarvangasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Lie on your back with your arms alongside your body, palms facing down.',
    'Engage your core and press your arms into the floor as you lift your legs toward the ceiling.',
    'Inhale and lift your hips, supporting your lower back with your hands.',
    'Walk your hands up your back toward your shoulder blades.',
    'Exhale and straighten your legs toward the ceiling, creating a vertical line.',
    'Keep your weight on your shoulders and upper arms, never on your neck.'
  ],
  exit_instructions = ARRAY[
    'Bend your knees toward your forehead.',
    'Support your back with your hands and slowly roll down, vertebra by vertebra.',
    'Rest with your legs extended or bent, taking several breaths before sitting up.'
  ],
  holding_cues = 'Keep your neck neutral and weight on your shoulders, not your neck. Engage your core and legs. Press your elbows toward each other to support your back.',
  breathing_pattern = 'Breathe deeply and evenly, holding for 30 seconds to several minutes.',
  has_side_variation = false
WHERE name_english = 'Shoulder Stand';

-- Pose 31: Staff Pose (Dandasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Sit on your mat with your legs extended straight in front of you.',
    'Flex your feet, pointing your toes toward the ceiling.',
    'Place your hands on the floor beside your hips with fingers pointing forward.',
    'Inhale and press through your hands to lift your chest and lengthen your spine.',
    'Engage your leg muscles and press your thighs into the floor.',
    'Draw your shoulder blades down your back and keep your chin parallel to the floor.'
  ],
  exit_instructions = ARRAY[
    'Release your hands from the floor.',
    'Relax your legs and shake them out gently.',
    'Move into your next seated pose.'
  ],
  holding_cues = 'Keep your spine straight and legs active. Press through your heels and lift through the crown of your head. Engage your core to support your lower back.',
  breathing_pattern = 'Breathe deeply and evenly, holding for 5-10 breaths.',
  has_side_variation = false
WHERE name_english = 'Staff Pose';

-- Pose 32: Reclined Bound Angle Pose (Supta Baddha Konasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Sit in Bound Angle Pose with the soles of your feet together.',
    'Place your hands behind you and slowly lower your back to the floor.',
    'Allow your knees to fall open naturally to the sides.',
    'Rest your arms alongside your body with palms facing up, or place one hand on your heart and one on your belly.',
    'Close your eyes and settle into the pose, making any final adjustments for comfort.',
    'Use props under your knees if your hips are tight.'
  ],
  exit_instructions = ARRAY[
    'Use your hands to gently bring your knees together.',
    'Roll to your right side and rest for a few breaths.',
    'Press yourself up to a seated position using your left hand.'
  ],
  holding_cues = 'Allow your hips to release naturally without forcing your knees toward the floor. Let your breath flow naturally. Relax completely into the support beneath you.',
  breathing_pattern = 'Breathe naturally and deeply, holding for 3-5 minutes or longer.',
  has_side_variation = false
WHERE name_english = 'Reclined Bound Angle Pose';

-- Pose 33: Legs Up the Wall (Viparita Karani)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Sit sideways next to a wall with your hip touching the wall.',
    'In one motion, swing your legs up the wall as you lower your back to the floor.',
    'Scoot your hips as close to the wall as is comfortable.',
    'Rest your arms alongside your body with palms facing up, or place them on your belly.',
    'Close your eyes and allow your body to relax completely.',
    'Adjust the distance from the wall based on your hamstring flexibility.'
  ],
  exit_instructions = ARRAY[
    'Bend your knees and place your feet on the wall.',
    'Push gently away from the wall and roll to your right side.',
    'Rest on your side for a few breaths before slowly sitting up.'
  ],
  holding_cues = 'Allow gravity to drain tension from your legs. Keep your chin slightly tucked and your neck long. Breathe naturally and let go of any effort.',
  breathing_pattern = 'Breathe slowly and naturally, resting for 5-15 minutes.',
  has_side_variation = false
WHERE name_english = 'Legs Up the Wall';

-- Pose 34: Happy Baby Pose (Ananda Balasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Lie on your back and draw your knees toward your chest.',
    'Inhale as you grasp the outside edges of your feet with your hands.',
    'Open your knees wider than your torso and bring them toward your armpits.',
    'Exhale and gently pull your feet down, bringing your knees closer to the floor.',
    'Keep your ankles directly over your knees, creating a 90-degree angle.',
    'Relax your shoulders on the floor and keep your tailbone grounded.'
  ],
  exit_instructions = ARRAY[
    'Release your feet and hug your knees to your chest.',
    'Rock gently side to side to massage your back.',
    'Extend your legs when ready or roll to one side to sit up.'
  ],
  holding_cues = 'Keep your lower back on the floor and your tailbone heavy. Gently pull on your feet to increase the stretch in your hips and groin. Relax your face and jaw.',
  breathing_pattern = 'Breathe deeply and naturally, holding for 1-2 minutes.',
  has_side_variation = false
WHERE name_english = 'Happy Baby Pose';

-- Pose 35: Sphinx Pose (Salamba Bhujangasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Lie on your belly with your legs extended and the tops of your feet pressing into the mat.',
    'Place your elbows under your shoulders with your forearms parallel on the floor.',
    'Inhale as you press through your forearms to lift your chest.',
    'Draw your shoulder blades down your back and lift through the crown of your head.',
    'Keep your lower ribs on the floor and engage your legs.',
    'Gaze forward, keeping your neck in a neutral position.'
  ],
  exit_instructions = ARRAY[
    'Exhale as you slowly lower your chest back to the mat.',
    'Turn your head to one side and rest your arms alongside your body.',
    'Take a few breaths before moving into your next pose.'
  ],
  holding_cues = 'Press firmly through your forearms and keep your shoulders away from your ears. Engage your back muscles gently. Breathe into your chest.',
  breathing_pattern = 'Breathe deeply and evenly, holding for 1-3 minutes.',
  has_side_variation = false
WHERE name_english = 'Sphinx Pose';

-- Pose 36: Seated Side Bend (Parsva Sukhasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Sit in Easy Pose with your legs crossed comfortably.',
    'Place your left hand on the floor beside your left hip.',
    'Inhale and extend your right arm up alongside your right ear.',
    'Exhale as you lean to the left, creating a gentle side bend.',
    'Keep both sit bones grounded and avoid twisting.',
    'Gaze up toward your extended arm or straight ahead.'
  ],
  exit_instructions = ARRAY[
    'Inhale as you bring your torso back to center.',
    'Exhale and lower your right arm.',
    'Prepare to repeat on the opposite side.'
  ],
  holding_cues = 'Keep both sit bones grounded and lengthen through the side of your body. Avoid collapsing into the bend. Breathe into the stretched side.',
  breathing_pattern = 'Breathe deeply, feeling expansion along your stretched side.',
  has_side_variation = true
WHERE name_english = 'Seated Side Bend';

-- Pose 37: Extended Puppy Pose (Uttana Shishosana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Begin on your hands and knees in tabletop position.',
    'Walk your hands forward, keeping your hips directly over your knees.',
    'Inhale to prepare, then exhale as you lower your chest toward the floor.',
    'Rest your forehead on the mat and extend your arms forward with palms down.',
    'Keep your elbows lifted off the floor.',
    'Allow your spine to arch naturally, creating a stretch through your shoulders and upper back.'
  ],
  exit_instructions = ARRAY[
    'Walk your hands back toward your body.',
    'Inhale as you lift your chest and return to tabletop position.',
    'Sit back in Child''s Pose to rest if needed.'
  ],
  holding_cues = 'Keep your hips over your knees and press your hands actively into the floor. Let your chest melt toward the earth. Breathe into your upper back and shoulders.',
  breathing_pattern = 'Breathe deeply and evenly, holding for 30-60 seconds.',
  has_side_variation = false
WHERE name_english = 'Extended Puppy Pose';

-- Pose 38: Supine Spinal Twist (Supta Matsyendrasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Lie on your back with your arms extended out to the sides in a T position.',
    'Draw your right knee toward your chest, keeping your left leg extended.',
    'Inhale to lengthen your spine.',
    'Exhale as you guide your right knee across your body to the left side.',
    'Turn your head to gaze over your right shoulder.',
    'Keep your right shoulder grounded as much as possible.'
  ],
  exit_instructions = ARRAY[
    'Inhale and bring your knee back to center.',
    'Exhale and extend your right leg to meet your left.',
    'Prepare to repeat on the opposite side.'
  ],
  holding_cues = 'Keep your shoulders grounded and relax into the twist. Let gravity gently deepen the stretch. Breathe into any areas of tightness.',
  breathing_pattern = 'Breathe deeply and naturally, holding for 1-2 minutes on each side.',
  has_side_variation = true
WHERE name_english = 'Supine Spinal Twist';

-- Pose 39: Garland Pose (Malasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Stand with your feet slightly wider than hip-width apart, toes turned out.',
    'Inhale and bring your hands to prayer position at your heart.',
    'Exhale as you bend your knees and lower your hips into a deep squat.',
    'Bring your elbows to the insides of your knees and press them apart.',
    'Lengthen your spine and lift your chest.',
    'Keep your heels on the floor if possible, or place a folded blanket under them for support.'
  ],
  exit_instructions = ARRAY[
    'Place your hands on the floor in front of you.',
    'Inhale as you straighten your legs, coming into a forward fold.',
    'Roll up to standing slowly, lifting your head last.'
  ],
  holding_cues = 'Press your elbows against your inner knees to open your hips. Keep your spine long and chest lifted. Ground through your feet.',
  breathing_pattern = 'Breathe deeply and evenly, holding for 30-60 seconds.',
  has_side_variation = false
WHERE name_english = 'Garland Pose';

-- Pose 40: Locust Pose (Salabhasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Lie on your belly with your arms alongside your body, palms facing up.',
    'Rest your forehead on the mat and press the tops of your feet into the floor.',
    'Inhale as you lift your head, chest, arms, and legs off the floor simultaneously.',
    'Reach back through your legs and forward through the crown of your head.',
    'Keep your gaze forward or slightly down to maintain a neutral neck.',
    'Engage your back muscles and glutes to support the lift.'
  ],
  exit_instructions = ARRAY[
    'Exhale as you slowly lower your chest, arms, and legs back to the mat.',
    'Turn your head to one side and rest your arms alongside your body.',
    'Take several breaths before moving on.'
  ],
  holding_cues = 'Keep your legs active and reaching back. Engage your core and back muscles. Lift from your upper back, not just your lower back.',
  breathing_pattern = 'Breathe steadily, holding for 5-8 breaths.',
  has_side_variation = false
WHERE name_english = 'Locust Pose';
