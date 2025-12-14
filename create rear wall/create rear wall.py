import adsk.core, adsk.fusion, traceback

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        design = app.activeProduct
        rootComp = design.rootComponent

        # Dimensions
        width = 1372  # mm
        height = 571  # mm
        thickness = 25  # mm
        hinge_radius = 12  # mm
        hinge_offset = 50  # mm from sides
        hinge_height = 20  # mm tall

        # Create rear wall sketch on rear plane (YZ)
        sketches = rootComp.sketches
        yzPlane = rootComp.yZConstructionPlane
        rearSketch = sketches.add(yzPlane)

        # Draw bottom rectangle profile (flush wall)
        pt0 = adsk.core.Point3D.create(0, 0, -width/2)
        pt1 = adsk.core.Point3D.create(0, height, width/2)
        rearSketch.sketchCurves.sketchLines.addTwoPointRectangle(pt0, pt1)

        # Finish sketch and create rear wall profile
        prof = rearSketch.profiles.item(0)
        loftInput = rootComp.features.loftFeatures.createInput(adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

        # Create guide curve by projecting roof profile if available
        roofBody = rootComp.bRepBodies.itemByName('roof')
        if not roofBody:
            ui.messageBox('Roof body not found. Please name your roof body "roof".')
            return

        roofTopFace = None
        for face in roofBody.faces:
            if face.geometry.surfaceType == adsk.core.SurfaceTypes.PlaneSurfaceType:
                # Use roughly horizontal face
                if abs(face.geometry.normal.z) > 0.9:
                    roofTopFace = face
                    break
        if not roofTopFace:
            ui.messageBox('No suitable horizontal face found on roof.')
            return

        # Create second sketch on rear roof face
        rearEdgeSketch = sketches.add(rootComp.xYConstructionPlane)
        rearEdgeSketch.project(roofTopFace)

        # Get top curve points for loft guide
        pt_top_left = adsk.core.Point3D.create(height, 0, -width/2)
        pt_top_right = adsk.core.Point3D.create(height, 0, width/2)
        rearSketch.sketchCurves.sketchLines.addLine(pt_top_left, pt_top_right)

        # Loft from rectangle to top edge
        rearWallProf = rearSketch.profiles.item(0)
        loftSections = loftInput.loftSections
        loftSections.add(rearWallProf)

        loftInput.isSolid = True
        loftInput.isClosed = False
        rearWallLoft = rootComp.features.loftFeatures.add(loftInput)
        rearWallBody = rearWallLoft.bodies.item(0)
        rearWallBody.name = 'Rear Wall'

        # Create 2 hinges on exterior top edge
        hingeSketch = sketches.add(yzPlane)
        y = height + hinge_radius
        for zOffset in [-width/2 + hinge_offset, width/2 - hinge_offset]:
            center = adsk.core.Point3D.create(0, y, zOffset)
            hingeSketch.sketchCurves.sketchCircles.addByCenterRadius(center, hinge_radius)

        hingeProf = hingeSketch.profiles
        extrudes = rootComp.features.extrudeFeatures
        for i in range(2):
            extInput = extrudes.createInput(hingeProf.item(i), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            dist = adsk.core.ValueInput.createByReal(thickness/2)
            extInput.setSymmetricExtent(dist, True)
            hinge = extrudes.add(extInput)
            hinge.bodies.item(0).name = f'Hinge {i+1}'

    except Exception as e:
        if ui:
            ui.messageBox('Script failed:\n{}'.format(traceback.format_exc()))
