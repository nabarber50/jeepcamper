import adsk.core, adsk.fusion, traceback

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        design = app.activeProduct
        root = design.rootComponent

        # Units in mm
        camper_length = 2743  # 9 feet
        camper_width = 1524   # 5 feet
        base_height = 100     # height of camper base (adjust as needed)
        hatch_width = 500
        hatch_length = 900
        wall_thickness = 30

        # Create a new sketch on the XZ plane (Top View)
        sketches = root.sketches
        top_plane = root.xZConstructionPlane
        top_sketch = sketches.add(top_plane)

        # Camper outer rectangle
        camper_rect = top_sketch.sketchCurves.sketchLines
        camper_points = [
            adsk.core.Point3D.create(0, 0, 0),
            adsk.core.Point3D.create(camper_length, 0, 0),
            adsk.core.Point3D.create(camper_length, camper_width, 0),
            adsk.core.Point3D.create(0, camper_width, 0)
        ]
        camper_rect.addFourPointRectangle(camper_points[0], camper_points[2])

        # Add roof panel cutouts
        hatch1 = top_sketch.sketchCurves.sketchLines.addCenterPointRectangle(
            adsk.core.Point3D.create(camper_length * 0.3, camper_width / 2, 0),
            adsk.core.Point3D.create((camper_length * 0.3) + hatch_length / 2, (camper_width / 2) + hatch_width / 2, 0)
        )
        hatch2 = top_sketch.sketchCurves.sketchLines.addCenterPointRectangle(
            adsk.core.Point3D.create(camper_length * 0.7, camper_width / 2, 0),
            adsk.core.Point3D.create((camper_length * 0.7) + hatch_length / 2, (camper_width / 2) + hatch_width / 2, 0)
        )

        # Extrude base
        prof = top_sketch.profiles.item(0)
        extrudes = root.features.extrudeFeatures
        base_extrude = extrudes.addSimple(prof, adsk.core.ValueInput.createByReal(base_height), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

        # Cut hatches
        for i in range(1, 3):
            hatch_prof = top_sketch.profiles.item(i)
            hatch_extrude = extrudes.addSimple(hatch_prof, adsk.core.ValueInput.createByReal(-base_height - 1),
                                               adsk.fusion.FeatureOperations.CutFeatureOperation)

        # Create side profile on YZ plane
        side_sketch = sketches.add(root.yZConstructionPlane)

        # Camper side wall outline
        wall_height = 1000
        wall_top_radius = 150
        wall_length = camper_width

        lines = side_sketch.sketchCurves.sketchLines
        wall_rect = lines.addCenterPointRectangle(
            adsk.core.Point3D.create(0, base_height + wall_height / 2, camper_width / 2),
            adsk.core.Point3D.create(wall_thickness / 2, base_height + wall_height, camper_width)
        )

        # Window
        window_width = 500
        window_height = 400
        window_center = adsk.core.Point3D.create(0, base_height + wall_height / 2, camper_width / 2)

        side_sketch.sketchCurves.sketchLines.addCenterPointRectangle(
            window_center,
            adsk.core.Point3D.create(window_center.x + window_width / 2, window_center.y + window_height / 2, window_center.z)
        )

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
