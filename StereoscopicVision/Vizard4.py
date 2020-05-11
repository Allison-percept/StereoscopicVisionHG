# Use vizfx module to load models and generate effects
import vizfx

# Load environment model
env = vizfx.addChild('gallery.osgb')

# Load avatar model
avatar = vizfx.addAvatar('vcc_male2.cfg')

# Add directional light
vizfx.addDirectionalLight(euler=(0,45,0))

