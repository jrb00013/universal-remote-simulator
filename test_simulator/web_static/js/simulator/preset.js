var DEFAULT_GRAPHICS_PRESET = {
    antialias: true,
    shadowMapEnabled: true,
    shadowMapType: 'PCFSoftShadowMap',
    shadowMapSize: 4096,
    shadowRadius: 6,
    castShadow: true,
    toneMappingExposure: 1.22,
    pixelRatio: 2.0,
    floorTextureWidth: 1024,
    floorTextureHeight: 512,
    wallTextureSize: 512,
    ceilingTextureSize: 256,
    fogFar: 52,
    ambientParticleCount: 150
};

// Read numeric preset value (allows 0 so SIM_SAFE / LOW tiers apply correctly)
function presetNum(preset, key, defaultVal) {
    var v = preset[key];
    if (typeof v === 'number' && !isNaN(v)) return v;
    var n = parseInt(v, 10);
    return (n === n) ? n : defaultVal;
}

// Initialize Three.js scene (uses window.GRAPHICS_PRESET from server when available)
