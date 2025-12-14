import adsk.core, adsk.fusion, adsk.cam, traceback

def create_rear_wall_with_hinge():
    app = adsk.core.Application.get()
    ui = app.userInterface
    design = app.activeProduct
    root = design.rootComponent

    try:
        # --- PARAMETERS ---
        wall_thickness = 15.0  # mm
        hinge_offset = 2.5     # mm gap from side walls
        hinge_diameter = 6.0   # mm
        rear_opening_width = 1200.0  # mm, adjust to your roof opening
        rear_opening_height = 700.0  # mm, adjust to your opening

        # --- CREATE REAR WALL SKETCH ---
        rear_plane = root.xYConstructionPlane
        rear_sketch = root.sketches.add(rear_plane)

        # Draw rectangle for rear wall
        rec_points = [
            adsk.core.Point3D.create(-rear_opening_width/2 + hinge_offset, 0, 0),
            adsk.core.Point3D.create(rear_opening_width/2 - hinge_offset, -rear_opening_height, 0)
        ]
        rear_sketch.sketchCurves.sketchLines.addTwoPointRectangle(rec_points[0], rec_points[1])

        # Extrude the rear wall
        rear_prof = rear_sketch.profiles.item(0)
        extrudes = root.features.extrudeFeatures
        rear_wall = extrudes.addSimple(rear_prof, adsk.core.ValueInput.createByReal(wall_thickness), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        rear_wall.name = 'Rear Wall'

        # --- CREATE HINGE BODY ---
        hinge_sketch = root.sketches.add(rear_plane)
        hinge_center = adsk.core.Point3D.create(0, wall_thickness, 0)
        hinge_sketch.sketchCurves.sketchCircles.addByCenterRadius(hinge_center, hinge_diameter/2)

        hinge_prof = hinge_sketch.profiles.item(0)
        hinge = extrudes.addSimple(hinge_prof, adsk.core.ValueInput.createByReal(rear_opening_width - (2 * hinge_offset)), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        hinge.name = 'Rear Hinge'

        # --- ADD REVOLUTE JOINT ---
        joint_input = root.joints.createInput(adsk.fusion.JointGeometry.createByPlanarFace(hinge.faces.item(0)), adsk.fusion.JointGeometry.createByPlanarFace(rear_wall.endFaces.item(0)), None)
        joint_input.setAsRevoluteJointMotion(adsk.fusion.JointDirections.XAxisJointDirection)
        joint = root.joints.add(joint_input)
        joint.name = 'Rear Wall Hinge'

        # Set hinge angle limits
        joint.motion.rotationLimits.isMinimumValueEnabled = True
        joint.motion.rotationLimits.minimumValue = 0  # closed
        joint.motion.rotationLimits.isMaximumValueEnabled = True
        joint.motion.rotationLimits.maximumValue = adsk.core.ValueInput.createByString('90 deg')

        ui.messageBox('Rear wall with hinge created successfully!')

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def run(context):
    create_rear_wall_with_hinge()
