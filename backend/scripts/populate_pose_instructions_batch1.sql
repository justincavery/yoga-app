-- Populate pose instructions for poses 1-20
-- This script adds detailed entry/exit instructions, holding cues, breathing patterns, and side variation flags
-- Run after applying the add_pose_instruction_fields migration

-- Batch 1: Poses 1-20

-- Pose 1: Mountain Pose (Tadasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Stand with your feet hip-width apart, allowing your arms to hang naturally by your sides.',
    'Inhale as you press all four corners of your feet firmly into the ground, feeling your connection to the earth.',
    'Engage your thigh muscles and gently lift your kneecaps, drawing energy up through your legs.',
    'Exhale as you lengthen your tailbone down toward the floor while lifting through the crown of your head.',
    'Roll your shoulders back and down, opening your chest and turning your palms to face forward.'
  ],
  exit_instructions = ARRAY[
    'Take a deep breath in, maintaining your alignment.',
    'Exhale as you gently release the pose, allowing your body to relax naturally.',
    'Step your feet together or move into your next pose with awareness.'
  ],
  holding_cues = 'Keep your weight evenly distributed across both feet. Maintain a gentle engagement in your core and legs while keeping your breath smooth and steady. Feel yourself growing taller with each inhale.',
  breathing_pattern = 'Breathe deeply and evenly, allowing 4-6 counts for each inhale and exhale.',
  has_side_variation = false
WHERE name_english = 'Mountain Pose';

-- Pose 2: Child''s Pose (Balasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Begin in a kneeling position with your big toes touching and knees hip-width apart or wider.',
    'Inhale to lengthen your spine, sitting up tall on your heels.',
    'Exhale as you fold forward, lowering your torso between your thighs.',
    'Rest your forehead gently on the mat and extend your arms forward with palms down, or rest them alongside your body with palms facing up.',
    'Allow your hips to sink back toward your heels, creating a gentle stretch through your spine.'
  ],
  exit_instructions = ARRAY[
    'Inhale as you walk your hands back toward your body.',
    'Exhale and slowly roll up to a seated position, lifting your head last.',
    'Take a moment to notice the effects of the pose before moving on.'
  ],
  holding_cues = 'Relax your shoulders and allow your back to expand with each breath. Let gravity gently stretch your spine. Keep your forehead soft and jaw relaxed.',
  breathing_pattern = 'Breathe naturally and deeply, feeling your back body expand with each inhale.',
  has_side_variation = false
WHERE name_english = 'Child''s Pose';

-- Pose 3: Downward Facing Dog (Adho Mukha Svanasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Start on your hands and knees with your wrists directly under your shoulders and knees under your hips.',
    'Spread your fingers wide and press firmly through your palms, especially through your index fingers and thumbs.',
    'Inhale to prepare, then exhale as you tuck your toes and lift your knees off the floor.',
    'Press your hips up and back, creating an inverted V shape with your body.',
    'Keep your knees slightly bent at first, focusing on lengthening your spine from your tailbone to the crown of your head.',
    'Gradually work your heels toward the floor without compromising the length in your spine.'
  ],
  exit_instructions = ARRAY[
    'Exhale as you bend your knees and lower them gently to the floor.',
    'Rest in Child''s Pose for a few breaths to allow your heart rate to normalize.',
    'Move mindfully into your next pose when ready.'
  ],
  holding_cues = 'Press actively through your hands and lift your hips high. Keep your head relaxed between your arms, not hanging down. Engage your core and keep your spine long.',
  breathing_pattern = 'Breathe steadily and deeply, maintaining 5-8 full breaths in the pose.',
  has_side_variation = false
WHERE name_english = 'Downward Facing Dog';

-- Pose 4: Cat-Cow Pose (Marjaryasana-Bitilasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Begin in tabletop position with your wrists under your shoulders and knees under your hips.',
    'Find a neutral spine with your gaze directed down at the floor.',
    'Inhale into Cow Pose: drop your belly toward the floor, lift your chest and chin, and gaze gently upward.',
    'Exhale into Cat Pose: draw your belly to your spine, round your back toward the ceiling, and tuck your chin to your chest.',
    'Continue flowing between these two poses, moving with your breath.'
  ],
  exit_instructions = ARRAY[
    'Return to a neutral tabletop position on an exhale.',
    'Sit back on your heels or move into Child''s Pose to rest.',
    'Take a few breaths to integrate the movement before continuing.'
  ],
  holding_cues = 'Move smoothly with your breath, creating a fluid wave-like motion through your spine. Keep your shoulders relaxed and away from your ears. Engage your core throughout.',
  breathing_pattern = 'Synchronize movement with breath: inhale for Cow Pose, exhale for Cat Pose. Flow for 5-10 complete breath cycles.',
  has_side_variation = false
WHERE name_english = 'Cat-Cow Pose';

-- Pose 5: Corpse Pose (Savasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Lie flat on your back with your legs extended and feet falling naturally apart, about hip-width distance.',
    'Place your arms alongside your body, palms facing up, about 6-8 inches away from your torso.',
    'Close your eyes gently and make any final adjustments to ensure complete comfort.',
    'Allow your feet to fall open naturally and let your fingers curl softly.',
    'Take a deep breath in, and as you exhale, allow your entire body to become heavy and relaxed.'
  ],
  exit_instructions = ARRAY[
    'Begin to deepen your breath, bringing gentle awareness back to your body.',
    'Wiggle your fingers and toes, then stretch your arms overhead for a full-body stretch.',
    'Roll to your right side, using your left hand to gently push yourself up to a seated position.',
    'Sit quietly for a few breaths before opening your eyes and moving on with your day.'
  ],
  holding_cues = 'Release all muscular effort and let the floor completely support you. Scan your body from toes to head, consciously releasing any remaining tension. Allow your breath to occur naturally.',
  breathing_pattern = 'Breathe naturally without controlling the breath. Let it become soft and effortless.',
  has_side_variation = false
WHERE name_english = 'Corpse Pose';

-- Pose 6: Easy Pose (Sukhasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Sit on your mat with your legs extended in front of you.',
    'Cross your legs at the shins, bringing each foot beneath the opposite knee.',
    'Rest your hands on your knees with palms facing down or up, whichever feels more comfortable.',
    'Inhale as you lengthen your spine, sitting up tall through the crown of your head.',
    'Gently draw your shoulder blades down your back and relax your shoulders.'
  ],
  exit_instructions = ARRAY[
    'Gently uncross your legs and extend them forward.',
    'Shake out your legs and switch the cross if you plan to sit again.',
    'Move mindfully into your next pose.'
  ],
  holding_cues = 'Keep your spine long and shoulders relaxed. Let your hips release and your sit bones ground into the earth. Maintain a soft gaze or close your eyes.',
  breathing_pattern = 'Breathe slowly and deeply, feeling your chest and belly expand with each inhale.',
  has_side_variation = false
WHERE name_english = 'Easy Pose';

-- Pose 7: Standing Forward Bend (Uttanasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Stand in Mountain Pose with your feet hip-width apart and hands on your hips.',
    'Inhale to lengthen your spine and engage your core.',
    'Exhale as you hinge forward from your hips, keeping your spine long as you fold.',
    'Let your hands release to the floor, blocks, or your shins, allowing your head and neck to relax completely.',
    'Bend your knees generously if you feel strain in your hamstrings or lower back.'
  ],
  exit_instructions = ARRAY[
    'Place your hands on your hips and engage your core muscles.',
    'Inhale as you rise up slowly with a flat back, pressing your feet firmly into the ground.',
    'Exhale and return to Mountain Pose, lifting your head last.'
  ],
  holding_cues = 'Let gravity draw you deeper into the fold. Keep your weight forward in your feet, not back in your heels. Relax your neck and jaw completely.',
  breathing_pattern = 'Breathe deeply, using each exhale to release a little deeper into the fold.',
  has_side_variation = false
WHERE name_english = 'Standing Forward Bend';

-- Pose 8: Warrior I (Virabhadrasana I)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'From standing, step your right foot back about 3-4 feet, turning your back foot out 45 degrees.',
    'Square your hips to face the front of your mat, adjusting your stance as needed.',
    'Inhale as you bend your front knee to 90 degrees, ensuring your knee stays over your ankle.',
    'Exhale as you sink your hips low while keeping your back leg strong and straight.',
    'Inhale and sweep your arms overhead, palms facing each other or touching, lifting through your chest.'
  ],
  exit_instructions = ARRAY[
    'Exhale as you lower your arms to your hips.',
    'Straighten your front leg and step your back foot forward to meet your front foot.',
    'Return to Mountain Pose and prepare to repeat on the opposite side.'
  ],
  holding_cues = 'Keep your front knee tracking over your ankle, not rolling inward. Press firmly through your back heel and lift through your chest. Keep your shoulders relaxed away from your ears.',
  breathing_pattern = 'Breathe steadily, maintaining strength and stability through 5-8 breaths.',
  has_side_variation = true
WHERE name_english = 'Warrior I';

-- Pose 9: Bridge Pose (Setu Bandha Sarvangasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Lie on your back with your knees bent and feet flat on the floor, hip-width apart.',
    'Position your feet close enough to your hips that you can brush your heels with your fingertips.',
    'Place your arms alongside your body with palms facing down.',
    'Inhale to prepare, pressing your feet and arms firmly into the floor.',
    'Exhale as you lift your hips toward the ceiling, rolling up vertebra by vertebra.',
    'Interlace your fingers beneath you and walk your shoulders closer together, or keep your arms by your sides.'
  ],
  exit_instructions = ARRAY[
    'Release your hands if they are interlaced and place your arms by your sides.',
    'Exhale as you slowly lower your spine to the mat, rolling down one vertebra at a time.',
    'Rest with your knees bent or extend your legs, taking a few breaths to integrate.'
  ],
  holding_cues = 'Press firmly through your feet and engage your glutes and thighs. Keep your knees parallel and tracking over your ankles. Lift your chest toward your chin without straining your neck.',
  breathing_pattern = 'Breathe deeply and evenly, maintaining the lift for 5-10 breaths.',
  has_side_variation = false
WHERE name_english = 'Bridge Pose';

-- Pose 10: Tree Pose (Vrksasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Begin in Mountain Pose with your weight evenly distributed on both feet.',
    'Shift your weight onto your left foot, pressing it firmly into the ground.',
    'Inhale as you bend your right knee and place your right foot on your left inner thigh, calf, or ankle (avoiding the knee).',
    'Find your balance, then bring your hands to prayer position at your heart center.',
    'When steady, exhale and extend your arms overhead like branches, palms together or separated.',
    'Fix your gaze on a non-moving point ahead to help maintain balance.'
  ],
  exit_instructions = ARRAY[
    'Lower your arms to prayer position at your heart.',
    'Exhale as you slowly lower your raised foot back to the ground.',
    'Return to Mountain Pose and prepare to repeat on the opposite side.'
  ],
  holding_cues = 'Press your foot and inner thigh firmly against each other. Keep your standing leg strong and your core engaged. Lengthen through your spine and keep your hips level.',
  breathing_pattern = 'Breathe slowly and steadily to help maintain your balance.',
  has_side_variation = true
WHERE name_english = 'Tree Pose';

-- Pose 11: Warrior II (Virabhadrasana II)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'From standing, step your feet wide apart, about 4-5 feet, extending your arms out to the sides at shoulder height.',
    'Turn your right foot out 90 degrees and your left foot in slightly.',
    'Inhale to lengthen your spine, then exhale as you bend your right knee to 90 degrees, keeping it over your ankle.',
    'Sink your hips low while keeping your torso upright and centered between your legs.',
    'Gaze over your right fingertips, keeping your shoulders relaxed and arms strong.'
  ],
  exit_instructions = ARRAY[
    'Inhale as you straighten your front leg.',
    'Exhale and lower your arms, turning your feet to face forward.',
    'Step your feet together and prepare to repeat on the opposite side.'
  ],
  holding_cues = 'Keep your front knee tracking over your ankle and your back leg straight and strong. Ground through the outer edge of your back foot. Stack your shoulders over your hips.',
  breathing_pattern = 'Breathe deeply and evenly, holding for 5-8 breaths while maintaining strong legs and a calm upper body.',
  has_side_variation = true
WHERE name_english = 'Warrior II';

-- Pose 12: Triangle Pose (Trikonasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'From standing, step your feet wide apart, about 4 feet, and extend your arms to shoulder height.',
    'Turn your right foot out 90 degrees and your left foot in slightly.',
    'Inhale to lengthen your spine, then exhale as you reach your right arm forward, shifting your hips back.',
    'Lower your right hand to your shin, ankle, or a block, and extend your left arm toward the ceiling.',
    'Rotate your torso open, stacking your shoulders, and gaze up at your left hand or straight ahead.'
  ],
  exit_instructions = ARRAY[
    'Inhale as you press firmly through your feet and engage your core to rise back up.',
    'Exhale and lower your arms, turning your feet to face forward.',
    'Step your feet together and prepare to repeat on the opposite side.'
  ],
  holding_cues = 'Keep both legs straight and active. Extend through both sides of your waist evenly. Press through your feet and lengthen through your fingertips.',
  breathing_pattern = 'Breathe fully and evenly, expanding through your chest with each inhale.',
  has_side_variation = true
WHERE name_english = 'Triangle Pose';

-- Pose 13: Extended Side Angle Pose (Utthita Parsvakonasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'From standing, step your feet wide apart, about 4-5 feet, and extend your arms at shoulder height.',
    'Turn your right foot out 90 degrees and your left foot in slightly.',
    'Inhale, then exhale as you bend your right knee to 90 degrees.',
    'Lower your right forearm to your right thigh or place your right hand on a block outside your right foot.',
    'Extend your left arm over your left ear, creating one long line from your left foot to your left fingertips.',
    'Gaze up toward your extended arm or straight ahead.'
  ],
  exit_instructions = ARRAY[
    'Inhale as you press through your feet and lift your torso back to center.',
    'Exhale and straighten your front leg, lowering your arms.',
    'Turn your feet forward and prepare to repeat on the opposite side.'
  ],
  holding_cues = 'Keep your front knee at 90 degrees and tracking over your ankle. Press through the outer edge of your back foot. Lengthen through the entire side body.',
  breathing_pattern = 'Breathe deeply, expanding through the side body with each inhale.',
  has_side_variation = true
WHERE name_english = 'Extended Side Angle Pose';

-- Pose 14: Seated Forward Bend (Paschimottanasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Sit on your mat with your legs extended straight in front of you and feet flexed.',
    'Inhale as you lift your arms overhead, lengthening your spine.',
    'Exhale as you hinge forward from your hips, keeping your spine long.',
    'Reach for your feet, ankles, or shins, allowing your head and neck to relax.',
    'With each exhale, gently release a little deeper into the fold, maintaining length in your spine.'
  ],
  exit_instructions = ARRAY[
    'Inhale as you engage your core and slowly roll up to seated, lifting your head last.',
    'Exhale and release your arms down by your sides.',
    'Take a moment to notice the effects before moving on.'
  ],
  holding_cues = 'Lead with your chest rather than rounding your back. Keep your legs active and your feet flexed. Relax your shoulders and breathe into your back body.',
  breathing_pattern = 'Breathe deeply, using each exhale to release deeper into the stretch.',
  has_side_variation = false
WHERE name_english = 'Seated Forward Bend';

-- Pose 15: Boat Pose (Navasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Sit on your mat with your knees bent and feet flat on the floor.',
    'Place your hands behind your thighs and lean back slightly, finding your balance on your sit bones.',
    'Inhale as you lift your feet off the floor, bringing your shins parallel to the ground.',
    'When stable, extend your arms forward at shoulder height, parallel to the floor.',
    'If you can maintain a straight spine, exhale and straighten your legs to form a V shape with your body.',
    'Keep your chest lifted and your core strongly engaged.'
  ],
  exit_instructions = ARRAY[
    'Exhale as you bend your knees and lower your feet to the floor.',
    'Release your arms down and sit up straight for a few breaths.',
    'Rest in Easy Pose or move into your next pose.'
  ],
  holding_cues = 'Keep your core engaged and your spine straight, not rounded. Focus on lifting your chest and drawing your shoulders back. Balance on your sit bones, not your tailbone.',
  breathing_pattern = 'Breathe steadily, maintaining the pose for 5-10 breaths despite the challenge.',
  has_side_variation = false
WHERE name_english = 'Boat Pose';

-- Pose 16: Cobra Pose (Bhujangasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Lie on your belly with your legs extended back and the tops of your feet pressing into the mat.',
    'Place your hands under your shoulders with your elbows close to your body.',
    'Press your thighs and the tops of your feet firmly into the floor.',
    'Inhale as you straighten your arms to lift your chest off the floor, keeping your elbows slightly bent.',
    'Roll your shoulders back and down, opening your chest forward.',
    'Keep your gaze forward and avoid crunching your neck by tilting your head back.'
  ],
  exit_instructions = ARRAY[
    'Exhale as you slowly lower your chest back to the mat.',
    'Turn your head to one side and rest your arms alongside your body.',
    'Take a few breaths to release before moving into your next pose.'
  ],
  holding_cues = 'Press firmly through your hands and engage your back muscles. Keep your shoulders away from your ears and your neck long. Engage your core to protect your lower back.',
  breathing_pattern = 'Breathe deeply into your chest, holding for 5-8 breaths.',
  has_side_variation = false
WHERE name_english = 'Cobra Pose';

-- Pose 17: Camel Pose (Ustrasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Kneel on your mat with your knees hip-width apart and your thighs perpendicular to the floor.',
    'Place your hands on your lower back with fingers pointing down, supporting your spine.',
    'Inhale as you lift your chest and begin to arch back, engaging your core and glutes.',
    'Exhale as you reach one hand at a time back to grasp your heels, or keep your hands on your lower back.',
    'Press your hips forward to stay over your knees and lift through your chest.',
    'Allow your head to release back only if it feels comfortable for your neck.'
  ],
  exit_instructions = ARRAY[
    'Bring your hands back to your lower back for support.',
    'Inhale and engage your core as you slowly lift your torso back to vertical, bringing your head up last.',
    'Sit back on your heels in Child''s Pose to rest and counter the backbend.'
  ],
  holding_cues = 'Keep your thighs perpendicular to the floor and your hips pressing forward. Engage your core and glutes to protect your lower back. Lift through your chest rather than simply dropping back.',
  breathing_pattern = 'Breathe deeply and steadily, holding for 5-8 breaths.',
  has_side_variation = false
WHERE name_english = 'Camel Pose';

-- Pose 18: Seated Spinal Twist (Ardha Matsyendrasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Sit on your mat with your legs extended in front of you.',
    'Bend your right knee and place your right foot flat on the floor outside your left knee.',
    'Keep your left leg extended or bend it and tuck your left foot near your right hip.',
    'Inhale as you lengthen your spine, reaching your left arm up.',
    'Exhale as you twist to the right, bringing your left elbow to the outside of your right knee.',
    'Place your right hand behind you for support and gaze over your right shoulder.'
  ],
  exit_instructions = ARRAY[
    'Exhale and slowly unwind from the twist, returning to center.',
    'Extend both legs forward and shake them out.',
    'Prepare to repeat on the opposite side.'
  ],
  holding_cues = 'Keep your spine long and lift through the crown of your head with each inhale. Deepen the twist with each exhale, but never force it. Keep both sit bones grounded.',
  breathing_pattern = 'Breathe evenly, using your inhales to lengthen and your exhales to deepen the twist.',
  has_side_variation = true
WHERE name_english = 'Seated Spinal Twist';

-- Pose 19: Dolphin Pose (Ardha Pincha Mayurasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'Begin on your hands and knees in tabletop position.',
    'Lower your forearms to the floor with elbows shoulder-width apart and palms flat.',
    'Interlace your fingers or keep your forearms parallel, whichever feels more stable.',
    'Inhale to prepare, then exhale as you tuck your toes and lift your hips up and back.',
    'Walk your feet slightly closer to your elbows, creating an inverted V shape.',
    'Keep your head off the floor, maintaining space between your ears and shoulders.'
  ],
  exit_instructions = ARRAY[
    'Exhale as you bend your knees and lower them gently to the floor.',
    'Rest in Child''s Pose for several breaths.',
    'Move mindfully into your next pose when ready.'
  ],
  holding_cues = 'Press firmly through your forearms and keep your shoulders stable. Engage your core and legs. Allow your head to hang naturally without resting on the floor.',
  breathing_pattern = 'Breathe deeply and evenly for 5-8 breaths.',
  has_side_variation = false
WHERE name_english = 'Dolphin Pose';

-- Pose 20: Pigeon Pose (Eka Pada Rajakapotasana)
UPDATE poses
SET
  entry_instructions = ARRAY[
    'From Downward Facing Dog, bring your right knee forward between your hands.',
    'Position your right shin on the floor with your right foot near your left hip.',
    'Extend your left leg straight back, pressing the top of your foot into the mat.',
    'Square your hips as much as possible toward the front of your mat.',
    'Inhale to lengthen your spine, then exhale as you fold forward over your front leg.',
    'Rest on your forearms or extend your arms forward, resting your forehead on the mat or a block.'
  ],
  exit_instructions = ARRAY[
    'Inhale as you walk your hands back toward your hips.',
    'Exhale and tuck your back toes, lifting your hips as you step back to Downward Facing Dog.',
    'Prepare to repeat on the opposite side.'
  ],
  holding_cues = 'Keep your hips as level as possible. Use props under your hip if needed. Relax into the stretch, breathing into any areas of tightness.',
  breathing_pattern = 'Breathe slowly and deeply, holding for 1-3 minutes on each side.',
  has_side_variation = true
WHERE name_english = 'Pigeon Pose';
