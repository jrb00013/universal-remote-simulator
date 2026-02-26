// 3D Virtual TV Simulator using Three.js
// Full Interactive 3D Experience with Remote Control

let scene, camera, renderer, controls;
let tvMesh, screenMesh, roomGroup, remoteMesh, remoteGroup;
let tvFrame, tvPowerLED, tvGlowLight;
let tvState = {};
let socket;
let irSignal = null;
let activeButton = null;
let buttonPressTime = 0;
let raycaster, mouse;

// Power animation state
let powerAnimation = {
    isAnimating: false,
    startTime: 0,
    duration: 2000, // 2 seconds for power on/off
    targetState: false,
    currentBrightness: 0,
    flickerPhase: 0,
    scanLinePosition: 0
};

// Channel change animation
let channelAnimation = {
    isAnimating: false,
    startTime: 0,
    duration: 800,
    oldChannel: 1,
    newChannel: 1,
    slideProgress: 0
};

// App switching animation
let appAnimation = {
    isAnimating: false,
    startTime: 0,
    duration: 2500, // Extended to 2.5 seconds for in-depth animations
    oldApp: 'Home',
    newApp: 'Home',
    fadeProgress: 0,
    phase: 'loading', // 'loading', 'logo', 'content'
    logoScale: 0,
    logoRotation: 0,
    logoOpacity: 0,
    particles: [],
    loadingProgress: 0,
    slideOffset: 0,
    zoomScale: 1
};

// Volume change animation
let volumeAnimation = {
    isAnimating: false,
    startTime: 0,
    duration: 500,
    oldVolume: 50,
    newVolume: 50,
    wavePhase: 0
};

// HDMI input switching animation
let hdmiAnimation = {
    isAnimating: false,
    startTime: 0,
    duration: 1500,
    oldInput: 'HDMI 1',
    newInput: 'HDMI 1',
    slideProgress: 0,
    fadeProgress: 0,
    logoScale: 0
};

// Channel overlay animation
let channelOverlay = {
    visible: false,
    startTime: 0,
    duration: 3000,
    channel: 1,
    opacity: 0,
    scale: 0,
    slideY: -50
};

// 3D UI elements
let ui3DElements = {
    channelOverlayMesh: null,
    hdmiOverlayMesh: null,
    volumeBarMesh: null,
    infoPanelMesh: null
};

// Screen effects
let screenEffects = {
    scanLines: true,
    pixelShimmer: true,
    vignette: true,
    reflection: true,
    colorShift: 0
};

// Initialize WebSocket connection
function initSocket() {
    socket = io();
    
    socket.on('connect', () => {
        console.log('Connected to server');
        document.getElementById('loading').style.display = 'none';
        // Initialize IR visualization
        if (typeof initIRVisualization === 'function') {
            initIRVisualization();
        }
        // Request initial state when connected
        socket.emit('request_state');
    });
    
    socket.on('tv_state_update', (state) => {
        updateTVState(state);
    });
    
    socket.on('connected', (data) => {
        console.log('Server:', data.message);
    });
}

// Update TV state and visual representation
function updateTVState(state) {
    const wasPoweredOn = tvState.powered_on;
    const oldChannel = tvState.channel;
    const oldApp = tvState.current_app;
    const oldVolume = tvState.volume;
    
    tvState = state;
    
    // Log power state changes
    if (wasPoweredOn !== state.powered_on) {
        console.log(`TV Power changed: ${wasPoweredOn} -> ${state.powered_on}`);
        
        // Start power animation
        startPowerAnimation(state.powered_on);
    }
    
    // Channel change animation
    if (oldChannel !== state.channel && state.powered_on) {
        startChannelAnimation(oldChannel, state.channel);
        showChannelOverlay(state.channel);
    }
    
    // App switching animation
    if (oldApp !== state.current_app && state.powered_on) {
        startAppAnimation(oldApp, state.current_app);
    }
    
    // HDMI input switching animation
    const oldInput = tvState.input_source;
    if (oldInput !== state.input_source && state.powered_on) {
        startHDMIAnimation(oldInput, state.input_source);
    }
    
    // Volume change animation
    if (Math.abs(oldVolume - state.volume) > 0 && state.powered_on) {
        startVolumeAnimation(oldVolume, state.volume);
    }
    
    // Update UI
    if (document.getElementById('power-status')) {
        document.getElementById('power-status').textContent = state.powered_on ? 'ON' : 'OFF';
        document.getElementById('power-status').className = `status-value ${state.powered_on ? 'on' : 'off'}`;
        document.getElementById('volume-status').textContent = state.volume + '%';
        document.getElementById('channel-status').textContent = state.channel;
        document.getElementById('app-status').textContent = state.current_app || 'Home';
        document.getElementById('mute-status').textContent = state.muted ? 'Yes' : 'No';
        document.getElementById('game-mode-status').textContent = state.game_mode ? 'ON' : 'OFF';
        
        if (state.last_button) {
            document.getElementById('last-button').textContent = state.last_button;
            // Trigger IR signal visualization
            if (state.last_button && state.last_button !== '-') {
                triggerIRSignal(state.last_button);
                
                // Start IR visualization (protocol, code, timeline, waveform)
                if (typeof startIRVisualization === 'function') {
                    const buttonCode = getButtonCodeFromName(state.last_button);
                    if (buttonCode !== null) {
                        startIRVisualization(buttonCode, state.last_button);
                    }
                }
            }
        }
    }
    
    // Show notification
    if (state.notification) {
        showNotification(state.notification);
    }
    
    // Update 3D TV screen (always update, especially on power change)
    updateTVScreen(state);
}

// Start power on/off animation
function startPowerAnimation(turningOn) {
    powerAnimation.isAnimating = true;
    powerAnimation.startTime = Date.now();
    powerAnimation.targetState = turningOn;
    powerAnimation.flickerPhase = 0;
    powerAnimation.currentBrightness = turningOn ? 0 : 1;
    powerAnimation.scanLinePosition = 0;
    
    console.log(`Starting power ${turningOn ? 'ON' : 'OFF'} animation`);
}

// Start channel change animation
function startChannelAnimation(oldCh, newCh) {
    channelAnimation.isAnimating = true;
    channelAnimation.startTime = Date.now();
    channelAnimation.oldChannel = oldCh;
    channelAnimation.newChannel = newCh;
    channelAnimation.slideProgress = 0;
}

// Get service-specific color
function getAppColor(appName) {
    const colors = {
        'YouTube': { r: 255, g: 0, b: 0 },
        'Netflix': { r: 229, g: 9, b: 20 },
        'Amazon Prime': { r: 0, g: 168, b: 225 },
        'HBO Max': { r: 128, g: 0, b: 128 },
        'Home': { r: 26, g: 26, b: 46 }
    };
    return colors[appName] || colors['Home'];
}

// Get service-specific logo text
function getAppLogo(appName) {
    const logos = {
        'YouTube': '▶',
        'Netflix': 'N',
        'Amazon Prime': 'PRIME',
        'HBO Max': 'HBO',
        'Home': 'HOME'
    };
    return logos[appName] || appName;
}

// Get button code from button name
function getButtonCodeFromName(buttonName) {
    const buttonMap = {
        'Power': 0x10,
        'Volume Up': 0x11,
        'Volume Down': 0x12,
        'Mute': 0x13,
        'Channel Up': 0x14,
        'Channel Down': 0x15,
        'Home': 0x20,
        'Menu': 0x21,
        'Back': 0x22,
        'Exit': 0x23,
        'Options': 0x24,
        'Input': 0x25,
        'Source': 0x26,
        'YouTube': 0x01,
        'Netflix': 0x02,
        'Amazon Prime': 0x03,
        'HBO Max': 0x04
    };
    return buttonMap[buttonName] || null;
}

// Start app switching animation with in-depth effects
function startAppAnimation(oldApp, newApp) {
    appAnimation.isAnimating = true;
    appAnimation.startTime = Date.now();
    appAnimation.oldApp = oldApp;
    appAnimation.newApp = newApp;
    appAnimation.fadeProgress = 0;
    appAnimation.phase = 'loading';
    appAnimation.logoScale = 0;
    appAnimation.logoRotation = 0;
    appAnimation.logoOpacity = 0;
    appAnimation.loadingProgress = 0;
    appAnimation.slideOffset = 0;
    appAnimation.zoomScale = 1;
    
    // Initialize particles for transition effect
    appAnimation.particles = [];
    const particleCount = 50;
    const newAppColor = getAppColor(newApp);
    for (let i = 0; i < particleCount; i++) {
        appAnimation.particles.push({
            x: Math.random() * 512,
            y: Math.random() * 512,
            vx: (Math.random() - 0.5) * 4,
            vy: (Math.random() - 0.5) * 4,
            size: Math.random() * 3 + 1,
            opacity: Math.random() * 0.8 + 0.2,
            color: newAppColor
        });
    }
}

// Start volume change animation
function startVolumeAnimation(oldVol, newVol) {
    volumeAnimation.isAnimating = true;
    volumeAnimation.startTime = Date.now();
    volumeAnimation.oldVolume = oldVol;
    volumeAnimation.newVolume = newVol;
    volumeAnimation.wavePhase = 0;
}

// IR signal particle system
let irParticles = null;
let irParticleSystem = null;

// Trigger IR signal visualization with enhanced effects
function triggerIRSignal(buttonName) {
    if (!remoteMesh || !tvMesh) return;
    
    // Remove existing IR signal
    if (irSignal) {
        scene.remove(irSignal);
        irSignal = null;
    }
    
    // Remove existing particles
    if (irParticleSystem) {
        scene.remove(irParticleSystem);
        irParticleSystem = null;
    }
    
    // Get remote position (IR emitter location)
    const remotePosition = new THREE.Vector3();
    remoteMesh.getWorldPosition(remotePosition);
    remotePosition.y += 0.1; // IR emitter on top of remote
    
    // Get TV position (IR receiver location)
    const tvPosition = new THREE.Vector3();
    tvMesh.getWorldPosition(tvPosition);
    tvPosition.y += 0.5; // IR receiver on TV
    
    // Create IR signal beam with multiple layers
    const direction = new THREE.Vector3().subVectors(tvPosition, remotePosition);
    const distance = direction.length();
    direction.normalize();
    
    // Main IR beam (core)
    const irGeometry = new THREE.ConeGeometry(0.03, distance, 16, 1, true);
    const irMaterial = new THREE.MeshBasicMaterial({
        color: 0xff0000,
        transparent: true,
        opacity: 0.8,
        side: THREE.DoubleSide
    });
    
    irSignal = new THREE.Mesh(irGeometry, irMaterial);
    irSignal.position.copy(remotePosition);
    irSignal.lookAt(tvPosition);
    irSignal.rotateX(Math.PI / 2);
    scene.add(irSignal);
    
    // Outer glow layer
    const glowGeometry = new THREE.ConeGeometry(0.08, distance, 16, 1, true);
    const glowMaterial = new THREE.MeshBasicMaterial({
        color: 0xff4444,
        transparent: true,
        opacity: 0.3,
        side: THREE.DoubleSide
    });
    const glowBeam = new THREE.Mesh(glowGeometry, glowMaterial);
    glowBeam.position.copy(remotePosition);
    glowBeam.lookAt(tvPosition);
    glowBeam.rotateX(Math.PI / 2);
    scene.add(glowBeam);
    
    // Create particle trail
    const particleCount = 50;
    const particles = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);
    
    for (let i = 0; i < particleCount; i++) {
        const t = i / particleCount;
        const pos = remotePosition.clone().lerp(tvPosition, t);
        positions[i * 3] = pos.x;
        positions[i * 3 + 1] = pos.y;
        positions[i * 3 + 2] = pos.z;
        
        // Red particles with varying intensity
        colors[i * 3] = 1.0; // R
        colors[i * 3 + 1] = 0.2 + (t * 0.3); // G
        colors[i * 3 + 2] = 0.1 + (t * 0.2); // B
    }
    
    particles.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    particles.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    
    const particleMaterial = new THREE.PointsMaterial({
        size: 0.05,
        vertexColors: true,
        transparent: true,
        opacity: 0.8,
        blending: THREE.AdditiveBlending
    });
    
    irParticleSystem = new THREE.Points(particles, particleMaterial);
    scene.add(irParticleSystem);
    
    // Animate IR signal with detailed effects
    let startTime = Date.now();
    const duration = 400; // 400ms for more visible effect
    
    function animateIR() {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        if (progress < 1) {
            // Core beam pulse
            const pulse = Math.sin(progress * Math.PI * 6) * 0.3 + 0.7;
            irSignal.material.opacity = 0.8 * pulse * (1 - progress * 0.5);
            irSignal.scale.set(1 + progress * 0.3, 1, 1);
            
            // Glow beam expansion
            glowBeam.material.opacity = 0.3 * (1 - progress);
            glowBeam.scale.set(1 + progress * 1.5, 1, 1);
            
            // Particle fade
            if (irParticleSystem) {
                const fadeProgress = progress;
                irParticleSystem.material.opacity = 0.8 * (1 - fadeProgress);
                
                // Animate particles (slight movement)
                const positions = irParticleSystem.geometry.attributes.position.array;
                for (let i = 0; i < particleCount; i++) {
                    const offset = Math.sin(progress * Math.PI * 2 + i) * 0.02;
                    positions[i * 3 + 1] += offset * 0.01;
                }
                irParticleSystem.geometry.attributes.position.needsUpdate = true;
            }
            
            requestAnimationFrame(animateIR);
        } else {
            // Remove IR signal and particles
            scene.remove(irSignal);
            scene.remove(glowBeam);
            if (irParticleSystem) {
                scene.remove(irParticleSystem);
            }
            irSignal = null;
            irParticleSystem = null;
        }
    }
    
    animateIR();
    
    // Highlight button on remote
    highlightRemoteButton(buttonName);
}

// Highlight button on remote control
function highlightRemoteButton(buttonName) {
    if (!remoteGroup) return;
    
    // Reset previous button
    if (activeButton) {
        activeButton.material.emissive.setHex(0x000000);
        activeButton.material.emissiveIntensity = 0;
        activeButton.position.z = 0.03;
    }
    
    // Button name mapping (handle variations)
    const buttonNameMap = {
        'Power': 'Power',
        'Volume Up': 'Volume Up',
        'Volume Down': 'Volume Down',
        'Channel Up': 'Channel Up',
        'Channel Down': 'Channel Down',
        'Home': 'Home',
        'Menu': 'Menu',
        'Back': 'Back',
        'YouTube': 'YouTube',
        'Netflix': 'Netflix',
        'Amazon Prime': 'Amazon Prime',
        'HBO Max': 'HBO Max',
        'Game Mode': 'Game Mode',
        '1': '1', '2': '2', '3': '3', '4': '4', '5': '5',
        '6': '6', '7': '7', '8': '8', '9': '9', '0': '0'
    };
    
    // Normalize button name
    const normalizedName = buttonNameMap[buttonName] || buttonName;
    
    // Find and highlight button
    remoteGroup.children.forEach(child => {
        if (child.userData && child.userData.buttonName) {
            // Exact match or partial match
            if (child.userData.buttonName === normalizedName || 
                child.userData.buttonName === buttonName ||
                buttonName.includes(child.userData.buttonName) ||
                child.userData.buttonName.includes(buttonName)) {
                activeButton = child;
                child.material.emissive.setHex(0x00ff00);
                child.material.emissiveIntensity = 1;
                buttonPressTime = Date.now();
                // Animate button press
                child.position.z = 0.02;
            }
        }
    });
}

// Show notification
function showNotification(message) {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.classList.add('show');
    
    setTimeout(() => {
        notification.classList.remove('show');
    }, 2000);
}

// Initialize Three.js scene
function initScene() {
    const container = document.getElementById('canvas-container');
    
    // Scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1a1a1a);
    scene.fog = new THREE.Fog(0x1a1a1a, 10, 50);
    
    // Camera
    camera = new THREE.PerspectiveCamera(
        75,
        window.innerWidth / window.innerHeight,
        0.1,
        1000
    );
    camera.position.set(0, 1.5, 5);
    
    // Renderer
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    container.appendChild(renderer.domElement);
    
    // Lights
    const ambientLight = new THREE.AmbientLight(0x404040, 0.5);
    scene.add(ambientLight);
    
    const mainLight = new THREE.DirectionalLight(0xffffff, 1);
    mainLight.position.set(5, 10, 5);
    mainLight.castShadow = true;
    mainLight.shadow.mapSize.width = 2048;
    mainLight.shadow.mapSize.height = 2048;
    scene.add(mainLight);
    
    const fillLight = new THREE.DirectionalLight(0xffffff, 0.3);
    fillLight.position.set(-5, 5, -5);
    scene.add(fillLight);
    
    // Point light for TV glow (will be animated)
    const tvGlow = new THREE.PointLight(0xffffff, 0, 10);
    tvGlow.position.set(0, 1.2, -8);
    scene.add(tvGlow);
    tvGlowLight = tvGlow; // Store reference for animation
    
    // Create room
    createRoom();
    
    // Create TV
    createTV();
    
    // Create 3D Remote Control
    createRemoteControl();
    
    // Initialize raycasting for interaction
    raycaster = new THREE.Raycaster();
    mouse = new THREE.Vector2();
    
    // Enhanced VR-like controls
    initControls();
    
    // Add subtle ambient effects
    addAmbientEffects();
    
    // Handle window resize
    window.addEventListener('resize', onWindowResize);
    
    // Start animation loop
    animate();
}

// Create room environment
function createRoom() {
    roomGroup = new THREE.Group();
    
    // Floor with texture pattern
    const floorGeometry = new THREE.PlaneGeometry(20, 20);
    const floorMaterial = new THREE.MeshStandardMaterial({
        color: 0x2a2a2a,
        roughness: 0.8,
        metalness: 0.2
    });
    const floor = new THREE.Mesh(floorGeometry, floorMaterial);
    floor.rotation.x = -Math.PI / 2;
    floor.position.y = 0;
    floor.receiveShadow = true;
    roomGroup.add(floor);
    
    // Back wall
    const wallGeometry = new THREE.PlaneGeometry(20, 10);
    const wallMaterial = new THREE.MeshStandardMaterial({
        color: 0x333333,
        roughness: 0.9
    });
    const backWall = new THREE.Mesh(wallGeometry, wallMaterial);
    backWall.position.z = -10;
    backWall.position.y = 5;
    roomGroup.add(backWall);
    
    // Side walls
    const leftWall = new THREE.Mesh(wallGeometry, wallMaterial);
    leftWall.rotation.y = Math.PI / 2;
    leftWall.position.x = -10;
    leftWall.position.y = 5;
    roomGroup.add(leftWall);
    
    const rightWall = new THREE.Mesh(wallGeometry, wallMaterial);
    rightWall.rotation.y = -Math.PI / 2;
    rightWall.position.x = 10;
    rightWall.position.y = 5;
    roomGroup.add(rightWall);
    
    // Ceiling
    const ceiling = new THREE.Mesh(floorGeometry, wallMaterial);
    ceiling.rotation.x = Math.PI / 2;
    ceiling.position.y = 10;
    roomGroup.add(ceiling);
    
    scene.add(roomGroup);
}

// Create 3D TV model
function createTV() {
    const tvGroup = new THREE.Group();
    
    // TV frame/bezel
    const frameGeometry = new THREE.BoxGeometry(3.2, 2, 0.2);
    const frameMaterial = new THREE.MeshStandardMaterial({
        color: 0x1a1a1a,
        roughness: 0.3,
        metalness: 0.7,
        emissive: 0x000000,
        emissiveIntensity: 0
    });
    const frame = new THREE.Mesh(frameGeometry, frameMaterial);
    frame.position.z = 0.1;
    frame.castShadow = true;
    tvGroup.add(frame);
    tvFrame = frame; // Store reference for animation
    
    // TV screen (the actual display)
    const screenGeometry = new THREE.PlaneGeometry(3, 1.8);
    // Create initial black texture
    const initialCanvas = document.createElement('canvas');
    initialCanvas.width = 512;
    initialCanvas.height = 512;
    const initialCtx = initialCanvas.getContext('2d');
    initialCtx.fillStyle = '#000000';
    initialCtx.fillRect(0, 0, initialCanvas.width, initialCanvas.height);
    const initialTexture = new THREE.CanvasTexture(initialCanvas);
    initialTexture.needsUpdate = true;
    
    const screenMaterial = new THREE.MeshStandardMaterial({
        color: 0xffffff,
        emissive: 0x000000,
        emissiveIntensity: 0,
        map: initialTexture,
        side: THREE.FrontSide,
        transparent: false
    });
    screenMesh = new THREE.Mesh(screenGeometry, screenMaterial);
    screenMesh.position.z = 0.11;
    tvGroup.add(screenMesh);
    
    // TV stand/base
    const standGeometry = new THREE.BoxGeometry(1.5, 0.3, 0.8);
    const standMaterial = new THREE.MeshStandardMaterial({
        color: 0x0a0a0a,
        roughness: 0.5,
        metalness: 0.3
    });
    const stand = new THREE.Mesh(standGeometry, standMaterial);
    stand.position.y = -1.15;
    stand.position.z = 0.2;
    stand.castShadow = true;
    tvGroup.add(stand);
    
    // IR receiver indicator (small LED)
    const irReceiverGeometry = new THREE.SphereGeometry(0.02, 8, 8);
    const irReceiverMaterial = new THREE.MeshBasicMaterial({
        color: 0x00ff00,
        emissive: 0x00ff00,
        emissiveIntensity: 0.5
    });
    const irReceiver = new THREE.Mesh(irReceiverGeometry, irReceiverMaterial);
    irReceiver.position.set(1.4, 0.8, 0.12);
    tvGroup.add(irReceiver);
    
    // Power indicator LED (red when off, green when on)
    const powerLEDGeometry = new THREE.SphereGeometry(0.015, 8, 8);
    const powerLEDMaterial = new THREE.MeshBasicMaterial({
        color: 0xff0000,
        emissive: 0xff0000,
        emissiveIntensity: 0.8
    });
    const powerLED = new THREE.Mesh(powerLEDGeometry, powerLEDMaterial);
    powerLED.position.set(-1.4, 0.8, 0.12);
    tvGroup.add(powerLED);
    tvPowerLED = powerLED; // Store reference for animation
    
    // Position TV in room
    tvGroup.position.set(0, 1.2, -8);
    tvGroup.rotation.y = 0;
    
    tvMesh = tvGroup;
    scene.add(tvMesh);
}

// Create 3D Remote Control
function createRemoteControl() {
    remoteGroup = new THREE.Group();
    
    // Remote body
    const bodyGeometry = new THREE.BoxGeometry(0.3, 0.8, 0.05);
    const bodyMaterial = new THREE.MeshStandardMaterial({
        color: 0x2a2a2a,
        roughness: 0.4,
        metalness: 0.1
    });
    const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
    body.castShadow = true;
    remoteGroup.add(body);
    remoteMesh = body;
    
    // Power button (top)
    const powerButton = createButton(0.08, 0.08, 0x10, 'Power', 0xff0000);
    powerButton.position.set(0, 0.3, 0.03);
    remoteGroup.add(powerButton);
    
    // Volume buttons
    const volUpButton = createButton(0.06, 0.06, 0x11, 'Volume Up', 0x4CAF50);
    volUpButton.position.set(-0.08, 0.15, 0.03);
    remoteGroup.add(volUpButton);
    
    const volDownButton = createButton(0.06, 0.06, 0x12, 'Volume Down', 0xf44336);
    volDownButton.position.set(-0.08, 0.05, 0.03);
    remoteGroup.add(volDownButton);
    
    // Channel buttons
    const chUpButton = createButton(0.06, 0.06, 0x14, 'Channel Up', 0x2196F3);
    chUpButton.position.set(0.08, 0.15, 0.03);
    remoteGroup.add(chUpButton);
    
    const chDownButton = createButton(0.06, 0.06, 0x15, 'Channel Down', 0x2196F3);
    chDownButton.position.set(0.08, 0.05, 0.03);
    remoteGroup.add(chDownButton);
    
    // Home button
    const homeButton = createButton(0.06, 0.06, 0x20, 'Home', 0xFFC107);
    homeButton.position.set(0, 0.1, 0.03);
    remoteGroup.add(homeButton);
    
    // Number pad (1-9)
    for (let i = 0; i < 9; i++) {
        const row = Math.floor(i / 3);
        const col = i % 3;
        const numButton = createButton(0.05, 0.05, 0x51 + i, `${i + 1}`, 0xffffff);
        numButton.position.set(
            (col - 1) * 0.07,
            -0.1 - row * 0.07,
            0.03
        );
        remoteGroup.add(numButton);
    }
    
    // Streaming service buttons (below number pad)
    const streamingButtons = [
        { name: 'YouTube', code: 0x01, color: 0xff0000, label: 'YT' },
        { name: 'Netflix', code: 0x02, color: 0xe50914, label: 'NF' },
        { name: 'Amazon Prime', code: 0x03, color: 0x00a8e1, label: 'PR' },
        { name: 'HBO Max', code: 0x04, color: 0x800080, label: 'HB' }
    ];
    
    for (let i = 0; i < streamingButtons.length; i++) {
        const btn = streamingButtons[i];
        const streamButton = createButton(0.06, 0.04, btn.code, btn.name, btn.color);
        streamButton.position.set(
            (i - 1.5) * 0.08,
            -0.35,
            0.03
        );
        remoteGroup.add(streamButton);
    }
    
    // IR emitter (red LED on top)
    const irEmitterGeometry = new THREE.SphereGeometry(0.015, 8, 8);
    const irEmitterMaterial = new THREE.MeshBasicMaterial({
        color: 0xff0000,
        emissive: 0xff0000,
        emissiveIntensity: 0.3
    });
    const irEmitter = new THREE.Mesh(irEmitterGeometry, irEmitterMaterial);
    irEmitter.position.set(0, 0.4, 0.03);
    remoteGroup.add(irEmitter);
    
    // Position remote in front of camera (on a virtual table)
    remoteGroup.position.set(2, 0.8, 2);
    remoteGroup.rotation.y = -Math.PI / 4;
    
    scene.add(remoteGroup);
}

// Create a button for the remote
function createButton(width, height, buttonCode, buttonName, color) {
    const buttonGeometry = new THREE.BoxGeometry(width, height, 0.02);
    const buttonMaterial = new THREE.MeshStandardMaterial({
        color: color,
        roughness: 0.6,
        metalness: 0.2,
        emissive: 0x000000,
        emissiveIntensity: 0
    });
    const button = new THREE.Mesh(buttonGeometry, buttonMaterial);
    button.userData.buttonCode = buttonCode;
    button.userData.buttonName = buttonName;
    button.castShadow = true;
    return button;
}

// Update TV screen content
function updateTVScreen(state) {
    if (!screenMesh) {
        console.warn('Screen mesh not initialized yet');
        return;
    }
    
    if (!state) {
        console.warn('No state provided to updateTVScreen');
        return;
    }
    
    // Get current animation brightness (for smooth transitions)
    const effectivePoweredOn = powerAnimation.isAnimating 
        ? powerAnimation.currentBrightness > 0.1 
        : state.powered_on;
    const brightness = powerAnimation.isAnimating 
        ? powerAnimation.currentBrightness 
        : (state.powered_on ? 1.0 : 0.0);
    
    // Create screen texture based on state
    const canvas = document.createElement('canvas');
    canvas.width = 512;
    canvas.height = 512;
    const ctx = canvas.getContext('2d');
    
    if (!ctx) {
        console.error('Failed to get canvas context');
        return;
    }
    
    if (!effectivePoweredOn || brightness < 0.1) {
        // Black screen when off (with possible flicker during animation)
        const blackLevel = powerAnimation.isAnimating && powerAnimation.targetState
            ? Math.min(255, powerAnimation.flickerPhase * 50) // Flicker effect
            : 0;
        ctx.fillStyle = `rgb(${blackLevel}, ${blackLevel}, ${blackLevel})`;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
    } else {
        // Screen content based on app (with brightness modulation and smooth transitions)
        const appColors = {
            'Home': '#1a1a2e',
            'YouTube': '#FF0000',
            'Netflix': '#E50914',
            'Amazon Prime': '#00A8E1',
            'HBO Max': '#800080'
        };
        
        // Smooth color transition during app switch
        let bgColor = appColors[state.current_app] || '#1a1a2e';
        let oldBgColor = appColors[appAnimation.oldApp] || '#1a1a2e';
        
        if (appAnimation.isAnimating) {
            const progress = appAnimation.fadeProgress;
            // Interpolate between old and new app colors
            const oldRgb = hexToRgb(oldBgColor);
            const newRgb = hexToRgb(bgColor);
            const rgb = {
                r: Math.floor(oldRgb.r + (newRgb.r - oldRgb.r) * progress),
                g: Math.floor(oldRgb.g + (newRgb.g - oldRgb.g) * progress),
                b: Math.floor(oldRgb.b + (newRgb.b - oldRgb.b) * progress)
            };
            bgColor = `rgb(${rgb.r}, ${rgb.g}, ${rgb.b})`;
        }
        
        const rgb = hexToRgb(bgColor);
        const brightRgb = {
            r: Math.floor(rgb.r * brightness),
            g: Math.floor(rgb.g * brightness),
            b: Math.floor(rgb.b * brightness)
        };
        
        // Base background with smooth color transition
        ctx.fillStyle = `rgb(${brightRgb.r}, ${brightRgb.g}, ${brightRgb.b})`;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Add gradient for depth (with brightness and color transition)
        const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
        gradient.addColorStop(0, `rgba(${brightRgb.r}, ${brightRgb.g}, ${brightRgb.b}, ${brightness})`);
        gradient.addColorStop(1, `rgba(0, 0, 0, ${brightness * 0.5})`);
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Channel change slide animation
        let channelX = 0;
        let channelOpacity = brightness;
        if (channelAnimation.isAnimating) {
            const elapsed = Date.now() - channelAnimation.startTime;
            const progress = Math.min(elapsed / channelAnimation.duration, 1);
            channelAnimation.slideProgress = progress;
            
            // Slide effect: old channel slides out left, new slides in from right
            const slideEase = 1 - Math.pow(1 - progress, 3); // Ease-out
            channelX = (slideEase - 0.5) * canvas.width * 2;
            channelOpacity = brightness * (1 - Math.abs(progress - 0.5) * 2);
        }
        
        // Channel number (only visible when bright enough)
        if (brightness > 0.3) {
            // Old channel (sliding out)
            if (channelAnimation.isAnimating && channelAnimation.slideProgress < 0.5) {
                ctx.save();
                ctx.globalAlpha = channelOpacity;
                ctx.fillStyle = `rgba(255, 255, 255, ${brightness})`;
                ctx.font = 'bold 48px Arial';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.translate(canvas.width / 2 + channelX, canvas.height / 2 - 100);
                ctx.fillText(`CH ${channelAnimation.oldChannel}`, 0, 0);
                ctx.restore();
            }
            
            // New channel (sliding in)
            ctx.save();
            ctx.globalAlpha = channelOpacity;
            ctx.fillStyle = `rgba(255, 255, 255, ${brightness})`;
            ctx.font = 'bold 48px Arial';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            const channelText = state.channel_input || `CH ${state.channel}`;
            ctx.translate(canvas.width / 2 + channelX, canvas.height / 2 - 100);
            ctx.fillText(channelText, 0, 0);
            ctx.restore();
            
            // In-depth streaming app animation
            if (appAnimation.isAnimating) {
                const phase = appAnimation.phase;
                const appColor = getAppColor(state.current_app);
                
                // Phase 1: Slide out old app
                if (phase === 'slideOut') {
                    ctx.save();
                    ctx.translate(canvas.width / 2 + appAnimation.slideOffset, canvas.height / 2);
                    ctx.scale(appAnimation.zoomScale, appAnimation.zoomScale);
                    ctx.globalAlpha = brightness * (1 - appAnimation.fadeProgress * 5);
                    ctx.font = 'bold 36px Arial';
                    ctx.fillStyle = `rgba(255, 255, 255, ${brightness})`;
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillText(appAnimation.oldApp || 'Home', 0, 0);
                    ctx.restore();
                }
                // Phase 2: Loading screen with particles
                else if (phase === 'loading') {
                    // Animated background with service color
                    const loadingColor = appColor;
                    const loadingGradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
                    loadingGradient.addColorStop(0, `rgba(${loadingColor.r}, ${loadingColor.g}, ${loadingColor.b}, ${brightness * 0.8})`);
                    loadingGradient.addColorStop(1, `rgba(0, 0, 0, ${brightness * 0.6})`);
                    ctx.fillStyle = loadingGradient;
                    ctx.fillRect(0, 0, canvas.width, canvas.height);
                    
                    // Draw particles
                    appAnimation.particles.forEach(p => {
                        ctx.save();
                        ctx.globalAlpha = p.opacity * brightness;
                        ctx.fillStyle = `rgba(${p.color.r}, ${p.color.g}, ${p.color.b}, 1)`;
                        ctx.beginPath();
                        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
                        ctx.fill();
                        ctx.restore();
                    });
                    
                    // Loading bar
                    const barWidth = canvas.width * 0.6;
                    const barHeight = 8;
                    const barX = (canvas.width - barWidth) / 2;
                    const barY = canvas.height * 0.7;
                    
                    // Background bar
                    ctx.fillStyle = `rgba(255, 255, 255, ${brightness * 0.2})`;
                    ctx.fillRect(barX, barY, barWidth, barHeight);
                    
                    // Progress bar
                    const progressWidth = barWidth * appAnimation.loadingProgress;
                    ctx.fillStyle = `rgba(${loadingColor.r}, ${loadingColor.g}, ${loadingColor.b}, ${brightness})`;
                    ctx.fillRect(barX, barY, progressWidth, barHeight);
                    
                    // Loading text
                    ctx.save();
                    ctx.globalAlpha = brightness;
                    ctx.font = '24px Arial';
                    ctx.fillStyle = `rgba(255, 255, 255, ${brightness})`;
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillText('Loading...', canvas.width / 2, barY - 30);
                    ctx.restore();
                }
                // Phase 3: Logo animation
                else if (phase === 'logo') {
                    // Background with service color
                    const logoColor = appColor;
                    const logoGradient = ctx.createRadialGradient(
                        canvas.width / 2, canvas.height / 2, 0,
                        canvas.width / 2, canvas.height / 2, canvas.width
                    );
                    logoGradient.addColorStop(0, `rgba(${logoColor.r}, ${logoColor.g}, ${logoColor.b}, ${brightness})`);
                    logoGradient.addColorStop(1, `rgba(0, 0, 0, ${brightness * 0.5})`);
                    ctx.fillStyle = logoGradient;
                    ctx.fillRect(0, 0, canvas.width, canvas.height);
                    
                    // Animated logo
                    ctx.save();
                    ctx.translate(canvas.width / 2, canvas.height / 2);
                    ctx.rotate(appAnimation.logoRotation);
                    ctx.scale(appAnimation.logoScale, appAnimation.logoScale);
                    ctx.globalAlpha = appAnimation.logoOpacity * brightness;
                    
                    // Logo shadow
                    ctx.shadowColor = 'rgba(0, 0, 0, 0.5)';
                    ctx.shadowBlur = 20;
                    ctx.shadowOffsetX = 5;
                    ctx.shadowOffsetY = 5;
                    
                    // Draw logo text
                    const logoText = getAppLogo(state.current_app);
                    ctx.font = `bold ${80 * appAnimation.logoScale}px Arial`;
                    ctx.fillStyle = `rgba(255, 255, 255, ${brightness})`;
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillText(logoText, 0, 0);
                    
                    // Service name below logo
                    ctx.font = `bold ${32 * appAnimation.logoScale}px Arial`;
                    ctx.fillText(state.current_app, 0, 60 * appAnimation.logoScale);
                    
                    ctx.restore();
                }
                // Phase 4: Content fade in
                else if (phase === 'content') {
                    // Final content with service color
                    const contentColor = appColor;
                    const contentGradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
                    contentGradient.addColorStop(0, `rgba(${contentColor.r}, ${contentColor.g}, ${contentColor.b}, ${brightness})`);
                    contentGradient.addColorStop(1, `rgba(0, 0, 0, ${brightness * 0.3})`);
                    ctx.fillStyle = contentGradient;
                    ctx.fillRect(0, 0, canvas.width, canvas.height);
                    
                    // App name with fade in
                    const contentOpacity = brightness * (1 - appAnimation.logoOpacity);
                    ctx.save();
                    ctx.globalAlpha = contentOpacity;
                    ctx.font = 'bold 48px Arial';
                    ctx.fillStyle = `rgba(255, 255, 255, ${brightness})`;
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillText(state.current_app || 'Home', canvas.width / 2, canvas.height / 2);
                    ctx.restore();
                }
            } else {
                // Static app display (no animation)
                ctx.save();
                ctx.globalAlpha = brightness;
                ctx.font = 'bold 36px Arial';
                ctx.fillStyle = `rgba(255, 255, 255, ${brightness})`;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(state.current_app || 'Home', canvas.width / 2, canvas.height / 2);
                ctx.restore();
            }
            
            // Volume bar with wave animation
            if (state.volume !== undefined) {
                let barWidth = (state.volume / 100) * 200;
                const volColor = state.muted ? 'rgba(244, 67, 54' : 'rgba(76, 175, 80';
                
                // Wave effect during volume change
                if (volumeAnimation.isAnimating) {
                    const elapsed = Date.now() - volumeAnimation.startTime;
                    const progress = Math.min(elapsed / volumeAnimation.duration, 1);
                    volumeAnimation.wavePhase = progress * Math.PI * 4;
                    const wave = Math.sin(volumeAnimation.wavePhase) * 0.1;
                    barWidth *= (1 + wave);
                }
                
                ctx.fillStyle = `${volColor}, ${brightness})`;
                ctx.fillRect(canvas.width / 2 - 100, canvas.height - 80, barWidth, 20);
                ctx.fillStyle = `rgba(255, 255, 255, ${brightness})`;
                ctx.font = '24px Arial';
                ctx.fillText(`${state.volume}%`, canvas.width / 2, canvas.height - 50);
            }
            
            // 3D Channel Overlay with animated UI
            if (channelOverlay.visible && brightness > 0.3) {
                ctx.save();
                ctx.translate(canvas.width / 2, 80 + channelOverlay.slideY);
                ctx.scale(channelOverlay.scale, channelOverlay.scale);
                ctx.globalAlpha = channelOverlay.opacity * brightness;
                
                // 3D box effect with gradient
                const overlayWidth = 200;
                const overlayHeight = 80;
                
                // Shadow
                ctx.shadowColor = 'rgba(0, 0, 0, 0.5)';
                ctx.shadowBlur = 20;
                ctx.shadowOffsetX = 5;
                ctx.shadowOffsetY = 5;
                
                // Background with gradient (3D effect)
                const overlayGradient = ctx.createLinearGradient(-overlayWidth/2, -overlayHeight/2, overlayWidth/2, overlayHeight/2);
                overlayGradient.addColorStop(0, 'rgba(30, 30, 50, 0.95)');
                overlayGradient.addColorStop(0.5, 'rgba(20, 20, 40, 0.95)');
                overlayGradient.addColorStop(1, 'rgba(10, 10, 30, 0.95)');
                ctx.fillStyle = overlayGradient;
                ctx.fillRect(-overlayWidth/2, -overlayHeight/2, overlayWidth, overlayHeight);
                
                // Border with glow
                ctx.strokeStyle = 'rgba(100, 150, 255, 0.8)';
                ctx.lineWidth = 3;
                ctx.strokeRect(-overlayWidth/2, -overlayHeight/2, overlayWidth, overlayHeight);
                
                // Channel number with 3D text effect
                ctx.shadowColor = 'rgba(100, 150, 255, 0.8)';
                ctx.shadowBlur = 10;
                ctx.fillStyle = 'rgba(255, 255, 255, 1)';
                ctx.font = 'bold 48px Arial';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(`CH ${channelOverlay.channel}`, 0, -5);
                
                // Channel label
                ctx.font = '20px Arial';
                ctx.fillStyle = 'rgba(200, 200, 200, 0.8)';
                ctx.fillText('Channel', 0, 25);
                
                ctx.restore();
            }
            
            // HDMI Input Switching Overlay
            if (hdmiAnimation.isAnimating && brightness > 0.3) {
                ctx.save();
                ctx.globalAlpha = brightness;
                
                // Phase 1: Fade out old input
                if (hdmiAnimation.fadeProgress < 1 && hdmiAnimation.logoScale === 0) {
                    ctx.globalAlpha = hdmiAnimation.fadeProgress * brightness;
                    ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
                    ctx.fillRect(0, 0, canvas.width, canvas.height);
                    
                    ctx.fillStyle = 'rgba(255, 255, 255, 1)';
                    ctx.font = 'bold 36px Arial';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillText(hdmiAnimation.oldInput, canvas.width / 2, canvas.height / 2);
                }
                // Phase 2: Show HDMI logo
                else if (hdmiAnimation.logoScale > 0 && hdmiAnimation.logoScale < 1) {
                    // Background
                    ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
                    ctx.fillRect(0, 0, canvas.width, canvas.height);
                    
                    // HDMI logo with scale animation
                    ctx.save();
                    ctx.translate(canvas.width / 2, canvas.height / 2);
                    ctx.scale(hdmiAnimation.logoScale, hdmiAnimation.logoScale);
                    
                    // HDMI icon (simplified)
                    ctx.fillStyle = 'rgba(100, 150, 255, 1)';
                    ctx.font = 'bold 80px Arial';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillText('HDMI', 0, -30);
                    
                    // Input number
                    ctx.font = 'bold 60px Arial';
                    ctx.fillText(hdmiAnimation.newInput.replace('HDMI ', ''), 0, 40);
                    
                    ctx.restore();
                }
                // Phase 3: Fade in new input
                else {
                    ctx.globalAlpha = hdmiAnimation.fadeProgress * brightness;
                    ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
                    ctx.fillRect(0, 0, canvas.width, canvas.height);
                    
                    ctx.fillStyle = 'rgba(255, 255, 255, 1)';
                    ctx.font = 'bold 36px Arial';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillText(hdmiAnimation.newInput, canvas.width / 2, canvas.height / 2);
                }
                
                ctx.restore();
            }
            
            // Static HDMI input display (when not animating)
            if (!hdmiAnimation.isAnimating && state.input_source && brightness > 0.5) {
                ctx.save();
                ctx.globalAlpha = brightness * 0.3;
                ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
                ctx.fillRect(canvas.width - 150, 10, 140, 30);
                ctx.fillStyle = 'rgba(255, 255, 255, 1)';
                ctx.font = '18px Arial';
                ctx.textAlign = 'right';
                ctx.textBaseline = 'top';
                ctx.fillText(state.input_source, canvas.width - 10, 15);
                ctx.restore();
            }
        }
        
        // Add scan lines effect (CRT-like)
        if (screenEffects.scanLines && brightness > 0.1) {
            // Animated scan line during power on (like old CRT TVs)
            if (powerAnimation.isAnimating && powerAnimation.targetState) {
                const scanY = powerAnimation.scanLinePosition * canvas.height;
                ctx.strokeStyle = `rgba(255, 255, 255, ${0.4 * brightness * powerAnimation.currentBrightness})`;
                ctx.lineWidth = 3;
                ctx.beginPath();
                ctx.moveTo(0, scanY);
                ctx.lineTo(canvas.width, scanY);
                ctx.stroke();
                
                // Add glow trail
                const glowGradient = ctx.createLinearGradient(0, scanY - 10, 0, scanY + 10);
                glowGradient.addColorStop(0, 'transparent');
                glowGradient.addColorStop(0.5, `rgba(255, 255, 255, ${0.2 * brightness * powerAnimation.currentBrightness})`);
                glowGradient.addColorStop(1, 'transparent');
                ctx.fillStyle = glowGradient;
                ctx.fillRect(0, scanY - 10, canvas.width, 20);
            }
            
            // Regular scan lines
            ctx.strokeStyle = `rgba(0, 0, 0, ${0.12 * brightness})`;
            ctx.lineWidth = 1;
            const scanLineSpacing = 3;
            const time = Date.now() * 0.001;
            const scanOffset = (time * 25) % scanLineSpacing;
            
            for (let y = scanOffset; y < canvas.height; y += scanLineSpacing) {
                ctx.beginPath();
                ctx.moveTo(0, y);
                ctx.lineTo(canvas.width, y);
                ctx.stroke();
            }
        }
        
        // Add pixel shimmer effect (sparkle)
        if (screenEffects.pixelShimmer && brightness > 0.5) {
            const time = Date.now() * 0.001;
            const shimmerIntensity = 0.08 * brightness;
            const pixelCount = 30;
            
            for (let i = 0; i < pixelCount; i++) {
                // Use seeded random for consistent pixel positions
                const seed = i * 1000;
                const x = (Math.sin(seed) * 0.5 + 0.5) * canvas.width;
                const y = (Math.cos(seed * 1.3) * 0.5 + 0.5) * canvas.height;
                
                // Animated shimmer
                const phase = (time * 3 + i * 0.5) % (Math.PI * 2);
                const alpha = (Math.sin(phase) + 1) * 0.5 * shimmerIntensity;
                
                if (alpha > 0.01) {
                    // Create glow effect
                    const glowGradient = ctx.createRadialGradient(x, y, 0, x, y, 4);
                    glowGradient.addColorStop(0, `rgba(255, 255, 255, ${alpha})`);
                    glowGradient.addColorStop(0.5, `rgba(255, 255, 255, ${alpha * 0.5})`);
                    glowGradient.addColorStop(1, 'transparent');
                    ctx.fillStyle = glowGradient;
                    ctx.fillRect(x - 4, y - 4, 8, 8);
                }
            }
        }
        
        // Add vignette effect (darker edges)
        if (screenEffects.vignette && brightness > 0.3) {
            const vignetteGradient = ctx.createRadialGradient(
                canvas.width / 2, canvas.height / 2, 0,
                canvas.width / 2, canvas.height / 2, canvas.width * 0.8
            );
            vignetteGradient.addColorStop(0, 'transparent');
            vignetteGradient.addColorStop(1, `rgba(0, 0, 0, ${0.3 * brightness})`);
            ctx.fillStyle = vignetteGradient;
            ctx.fillRect(0, 0, canvas.width, canvas.height);
        }
        
        // Add screen reflection (subtle)
        if (screenEffects.reflection && brightness > 0.5) {
            const reflectionGradient = ctx.createLinearGradient(0, 0, 0, canvas.height * 0.3);
            reflectionGradient.addColorStop(0, `rgba(255, 255, 255, ${0.1 * brightness})`);
            reflectionGradient.addColorStop(1, 'transparent');
            ctx.fillStyle = reflectionGradient;
            ctx.fillRect(0, 0, canvas.width, canvas.height * 0.3);
        }
    }
    
    // Update screen material
    const texture = new THREE.CanvasTexture(canvas);
    texture.needsUpdate = true;
    
    // Dispose old texture to prevent memory leaks
    if (screenMesh.material.map) {
        screenMesh.material.map.dispose();
    }
    
    screenMesh.material.map = texture;
    
    // Update emissive properties for screen glow (with animation)
    screenMesh.material.emissive = new THREE.Color(0xffffff);
    screenMesh.material.emissiveIntensity = brightness;
    screenMesh.material.color = new THREE.Color(brightness, brightness, brightness);
    
    screenMesh.material.needsUpdate = true;
}

// Helper function to convert hex to RGB
function hexToRgb(hex) {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
    } : { r: 26, g: 26, b: 46 }; // Default dark blue
}

// Enhanced VR-like controls with smooth movement
function initControls() {
    let isDragging = false;
    let previousMousePosition = { x: 0, y: 0 };
    let cameraDistance = 5;
    let targetCameraPosition = new THREE.Vector3(0, 1.5, 5);
    let currentCameraPosition = targetCameraPosition.clone();
    
    const canvas = renderer.domElement;
    
    // Mouse click for remote interaction
    canvas.addEventListener('click', (e) => {
        mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
        mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;
        
        raycaster.setFromCamera(mouse, camera);
        const intersects = raycaster.intersectObjects(remoteGroup.children, true);
        
        if (intersects.length > 0) {
            const button = intersects[0].object;
            if (button.userData.buttonCode !== undefined) {
                // Visual feedback: highlight button immediately
                highlightRemoteButton(button.userData.buttonName);
                
                // Trigger IR signal visualization
                triggerIRSignal(button.userData.buttonName);
                
                // Send button press via WebSocket
                if (socket && socket.connected) {
                    socket.emit('button_press', { button_code: button.userData.buttonCode });
                    console.log(`Clicked button: ${button.userData.buttonName} (0x${button.userData.buttonCode.toString(16).toUpperCase()})`);
                } else {
                    console.warn('WebSocket not connected, button press not sent to server');
                }
            }
        }
    });
    
    canvas.addEventListener('mousedown', (e) => {
        isDragging = true;
        previousMousePosition = { x: e.clientX, y: e.clientY };
        canvas.style.cursor = 'grabbing';
    });
    
    canvas.addEventListener('mousemove', (e) => {
        if (!isDragging) {
            // Check for button hover
            mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
            mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;
            raycaster.setFromCamera(mouse, camera);
            const intersects = raycaster.intersectObjects(remoteGroup.children, true);
            
            if (intersects.length > 0 && intersects[0].object.userData.buttonCode !== undefined) {
                canvas.style.cursor = 'pointer';
            } else {
                canvas.style.cursor = 'grab';
            }
            return;
        }
        
        const deltaX = e.clientX - previousMousePosition.x;
        const deltaY = e.clientY - previousMousePosition.y;
        
        // Rotate camera around TV (VR-like orbit)
        const angleX = deltaY * 0.01;
        const angleY = deltaX * 0.01;
        
        cameraDistance = currentCameraPosition.distanceTo(new THREE.Vector3(0, 1.2, -8));
        const spherical = new THREE.Spherical();
        spherical.setFromVector3(currentCameraPosition.clone().sub(new THREE.Vector3(0, 1.2, -8)));
        spherical.theta -= angleY;
        spherical.phi += angleX;
        spherical.phi = Math.max(0.1, Math.min(Math.PI - 0.1, spherical.phi));
        
        targetCameraPosition = new THREE.Vector3();
        targetCameraPosition.setFromSpherical(spherical);
        targetCameraPosition.add(new THREE.Vector3(0, 1.2, -8));
        
        previousMousePosition = { x: e.clientX, y: e.clientY };
    });
    
    canvas.addEventListener('mouseup', () => {
        isDragging = false;
        canvas.style.cursor = 'grab';
    });
    
    canvas.style.cursor = 'grab';
    
    canvas.addEventListener('wheel', (e) => {
        e.preventDefault();
        cameraDistance += e.deltaY * 0.01;
        cameraDistance = Math.max(2, Math.min(15, cameraDistance));
        
        const direction = currentCameraPosition.clone().sub(new THREE.Vector3(0, 1.2, -8)).normalize();
        targetCameraPosition = new THREE.Vector3(0, 1.2, -8).add(direction.multiplyScalar(cameraDistance));
    });
    
    // Camera presets
    window.addEventListener('keydown', (e) => {
        if (e.code === 'Space') {
            e.preventDefault();
            targetCameraPosition.set(0, 1.5, 5);
        } else if (e.code === 'Digit1') {
            // Front view
            targetCameraPosition.set(0, 1.5, 5);
        } else if (e.code === 'Digit2') {
            // Side view
            targetCameraPosition.set(5, 1.5, 0);
        } else if (e.code === 'Digit3') {
            // Top view
            targetCameraPosition.set(0, 8, 0);
        } else if (e.code === 'Digit4') {
            // Remote close-up
            targetCameraPosition.set(2, 0.8, 3);
        }
    });
    
    // Smooth camera interpolation
    function updateCamera() {
        currentCameraPosition.lerp(targetCameraPosition, 0.1);
        camera.position.copy(currentCameraPosition);
        camera.lookAt(0, 1.2, -8);
    }
    
    // Store update function for animation loop
    window.updateCamera = updateCamera;
}

// Animation loop with smooth camera movement
function animate() {
    requestAnimationFrame(animate);
    
    // Smooth camera interpolation
    if (window.updateCamera) {
        window.updateCamera();
    }
    
    // Power on/off animation
    if (powerAnimation.isAnimating && screenMesh) {
        const elapsed = Date.now() - powerAnimation.startTime;
        const progress = Math.min(elapsed / powerAnimation.duration, 1);
        
        // Animate scan line during power on (for visual effect)
        if (powerAnimation.targetState) {
            powerAnimation.scanLinePosition = progress;
        }
        
        if (powerAnimation.targetState) {
            // Power ON animation: detailed multi-phase sequence
            if (progress < 0.05) {
                // Phase 1: Initial power surge (very brief flash)
                powerAnimation.flickerPhase = Math.random() > 0.8 ? 1 : 0;
                powerAnimation.currentBrightness = powerAnimation.flickerPhase * 0.4;
            } else if (progress < 0.15) {
                // Phase 2: Multiple flickers (like CRT warming up)
                const flickerRate = Math.sin(progress * Math.PI * 20) * 0.5 + 0.5;
                powerAnimation.flickerPhase = flickerRate;
                powerAnimation.currentBrightness = 0.1 + (flickerRate * 0.3);
            } else if (progress < 0.35) {
                // Phase 3: Scan line effect (like old TVs)
                const scanProgress = (progress - 0.15) / 0.2;
                powerAnimation.flickerPhase = 0.5 + (scanProgress * 0.3);
                powerAnimation.currentBrightness = 0.3 + (scanProgress * 0.2);
            } else if (progress < 0.6) {
                // Phase 4: Color stabilization
                const stabilizeProgress = (progress - 0.35) / 0.25;
                const eased = 1 - Math.pow(1 - stabilizeProgress, 2);
                powerAnimation.currentBrightness = 0.5 + (eased * 0.3);
                powerAnimation.flickerPhase = 0.8 + (eased * 0.2);
            } else {
                // Phase 5: Final smooth fade to full brightness
                const fadeProgress = (progress - 0.6) / 0.4;
                // Ease-out curve for smooth transition
                const eased = 1 - Math.pow(1 - fadeProgress, 3);
                powerAnimation.currentBrightness = 0.8 + (eased * 0.2);
                powerAnimation.flickerPhase = 1;
            }
            
            // Animate bezel glow with pulsing
            if (tvFrame && tvFrame.material) {
                const baseGlow = powerAnimation.currentBrightness * 0.15;
                const pulse = Math.sin(progress * Math.PI * 4) * 0.05;
                const glowIntensity = Math.max(0, baseGlow + pulse);
                tvFrame.material.emissive.setHex(0xffffff);
                tvFrame.material.emissiveIntensity = glowIntensity;
                
                // Subtle color shift during power on
                const colorShift = progress * 0.1;
                tvFrame.material.color.setRGB(1 - colorShift, 1 - colorShift * 0.5, 1);
            }
            
            // Animate TV glow light with smooth ramp
            if (tvGlowLight) {
                const lightIntensity = powerAnimation.currentBrightness * 1.2;
                tvGlowLight.intensity = Math.min(lightIntensity, 1.5);
                
                // Color temperature shift (warmer when turning on)
                const colorTemp = 1.0 - (progress * 0.2);
                tvGlowLight.color.setRGB(1, colorTemp, colorTemp * 0.9);
            }
            
            // Animate power LED (red -> green transition)
            if (tvPowerLED && tvPowerLED.material) {
                const ledProgress = Math.min(progress * 2, 1); // Faster transition
                if (ledProgress < 0.5) {
                    // Red to orange
                    tvPowerLED.material.color.setHex(0xff4400);
                    tvPowerLED.material.emissive.setHex(0xff4400);
                } else {
                    // Orange to green
                    const greenProgress = (ledProgress - 0.5) * 2;
                    const r = Math.floor(255 * (1 - greenProgress));
                    const g = Math.floor(255 * greenProgress);
                    tvPowerLED.material.color.setRGB(r / 255, g / 255, 0);
                    tvPowerLED.material.emissive.setRGB(r / 255, g / 255, 0);
                }
                tvPowerLED.material.emissiveIntensity = 0.8 + (powerAnimation.currentBrightness * 0.2);
            }
        } else {
            // Power OFF animation: detailed fade sequence
            const fadeProgress = 1 - progress;
            
            if (progress < 0.2) {
                // Phase 1: Quick dim
                const quickDim = 1 - (progress / 0.2);
                powerAnimation.currentBrightness = 0.7 + (quickDim * 0.3);
            } else if (progress < 0.5) {
                // Phase 2: Gradual fade
                const gradualProgress = (progress - 0.2) / 0.3;
                const eased = Math.pow(gradualProgress, 1.5);
                powerAnimation.currentBrightness = 0.7 * (1 - eased);
            } else {
                // Phase 3: Final fade to black
                const finalProgress = (progress - 0.5) / 0.5;
                const eased = Math.pow(finalProgress, 2);
                powerAnimation.currentBrightness = 0.7 * (1 - eased);
            }
            
            powerAnimation.flickerPhase = fadeProgress;
            powerAnimation.scanLinePosition = fadeProgress;
            
            // Animate bezel glow fade
            if (tvFrame && tvFrame.material) {
                tvFrame.material.emissiveIntensity = eased * 0.1;
            }
            
            // Animate TV glow light fade
            if (tvGlowLight) {
                tvGlowLight.intensity = eased * 0.8;
            }
            
            // Animate power LED (green -> red transition)
            if (tvPowerLED && tvPowerLED.material) {
                const ledProgress = 1 - fadeProgress;
                if (ledProgress > 0.5) {
                    // Green to orange
                    const orangeProgress = (ledProgress - 0.5) * 2;
                    const g = Math.floor(255 * (1 - orangeProgress));
                    const r = Math.floor(255 * orangeProgress);
                    tvPowerLED.material.color.setRGB(r / 255, g / 255, 0);
                    tvPowerLED.material.emissive.setRGB(r / 255, g / 255, 0);
                } else {
                    // Orange to red
                    tvPowerLED.material.color.setHex(0xff0000);
                    tvPowerLED.material.emissive.setHex(0xff0000);
                }
                tvPowerLED.material.emissiveIntensity = 0.8 * fadeProgress;
            }
        }
        
        // Update screen during animation (this will use currentBrightness)
        updateTVScreen(tvState);
        
        // End animation
        if (progress >= 1) {
            powerAnimation.isAnimating = false;
            powerAnimation.currentBrightness = powerAnimation.targetState ? 1.0 : 0.0;
            powerAnimation.scanLinePosition = 0;
            
            // Finalize LED state
            if (tvPowerLED && tvPowerLED.material) {
                if (powerAnimation.targetState) {
                    tvPowerLED.material.color.setHex(0x00ff00);
                    tvPowerLED.material.emissive.setHex(0x00ff00);
                    tvPowerLED.material.emissiveIntensity = 1.0;
                } else {
                    tvPowerLED.material.color.setHex(0xff0000);
                    tvPowerLED.material.emissive.setHex(0xff0000);
                    tvPowerLED.material.emissiveIntensity = 0.8;
                }
            }
            
            updateTVScreen(tvState);
            console.log(`Power animation complete: ${powerAnimation.targetState ? 'ON' : 'OFF'}`);
        }
    } else if (!powerAnimation.isAnimating && tvPowerLED && tvPowerLED.material) {
        // Update LED based on current state (when not animating)
        if (tvState.powered_on) {
            tvPowerLED.material.color.setHex(0x00ff00);
            tvPowerLED.material.emissive.setHex(0x00ff00);
            tvPowerLED.material.emissiveIntensity = 1.0;
        } else {
            tvPowerLED.material.color.setHex(0xff0000);
            tvPowerLED.material.emissive.setHex(0xff0000);
            tvPowerLED.material.emissiveIntensity = 0.8;
        }
    }
    
    // Channel change animation
    if (channelAnimation.isAnimating) {
        const elapsed = Date.now() - channelAnimation.startTime;
        const progress = Math.min(elapsed / channelAnimation.duration, 1);
        channelAnimation.slideProgress = progress;
        
        if (progress >= 1) {
            channelAnimation.isAnimating = false;
        }
        // Screen updates continuously during animation
        updateTVScreen(tvState);
    }
    
    // App switching animation - In-depth multi-phase animation
    if (appAnimation.isAnimating) {
        const elapsed = Date.now() - appAnimation.startTime;
        const progress = Math.min(elapsed / appAnimation.duration, 1);
        appAnimation.fadeProgress = progress;
        
        // Phase 1: Slide out old app (0-20%)
        if (progress < 0.2) {
            appAnimation.phase = 'slideOut';
            const phaseProgress = progress / 0.2;
            appAnimation.slideOffset = -phaseProgress * 512; // Slide left
            appAnimation.zoomScale = 1 - phaseProgress * 0.2; // Slight zoom out
        }
        // Phase 2: Loading screen with particles (20-50%)
        else if (progress < 0.5) {
            appAnimation.phase = 'loading';
            const phaseProgress = (progress - 0.2) / 0.3;
            appAnimation.loadingProgress = phaseProgress;
            appAnimation.slideOffset = -512; // Fully off screen
            appAnimation.zoomScale = 0.8;
            
            // Update particles
            appAnimation.particles.forEach(p => {
                p.x += p.vx;
                p.y += p.vy;
                p.opacity *= 0.98; // Fade out
                if (p.x < 0 || p.x > 512) p.vx *= -1;
                if (p.y < 0 || p.y > 512) p.vy *= -1;
            });
        }
        // Phase 3: Logo animation (50-75%)
        else if (progress < 0.75) {
            appAnimation.phase = 'logo';
            const phaseProgress = (progress - 0.5) / 0.25;
            // Logo scales in with bounce
            const eased = 1 - Math.pow(1 - phaseProgress, 3);
            appAnimation.logoScale = eased;
            appAnimation.logoRotation = eased * Math.PI * 2; // Full rotation
            appAnimation.logoOpacity = Math.min(1, eased * 1.2);
            appAnimation.loadingProgress = 1;
            appAnimation.slideOffset = 0;
            appAnimation.zoomScale = 0.8 + (eased * 0.2);
        }
        // Phase 4: Content fade in (75-100%)
        else {
            appAnimation.phase = 'content';
            const phaseProgress = (progress - 0.75) / 0.25;
            appAnimation.logoScale = 1;
            appAnimation.logoOpacity = 1 - phaseProgress; // Fade out logo
            appAnimation.slideOffset = 0;
            appAnimation.zoomScale = 1;
        }
        
        if (progress >= 1) {
            appAnimation.isAnimating = false;
            appAnimation.phase = 'content';
            appAnimation.logoOpacity = 0;
            appAnimation.slideOffset = 0;
            appAnimation.zoomScale = 1;
        }
        // Screen updates continuously during animation
        updateTVScreen(tvState);
    }
    
    // Volume change animation
    if (volumeAnimation.isAnimating) {
        const elapsed = Date.now() - volumeAnimation.startTime;
        const progress = Math.min(elapsed / volumeAnimation.duration, 1);
        // Wave animation
        volumeAnimation.wavePhase = progress * Math.PI * 4;
        
        if (progress >= 1) {
            volumeAnimation.isAnimating = false;
        }
        // Screen updates continuously during animation
        updateTVScreen(tvState);
    }
    
    // HDMI input switching animation
    if (hdmiAnimation.isAnimating) {
        const elapsed = Date.now() - hdmiAnimation.startTime;
        const progress = Math.min(elapsed / hdmiAnimation.duration, 1);
        
        // Phase 1: Fade out old input (0-30%)
        if (progress < 0.3) {
            hdmiAnimation.fadeProgress = 1 - (progress / 0.3);
            hdmiAnimation.slideProgress = progress / 0.3;
        }
        // Phase 2: Show HDMI logo (30-60%)
        else if (progress < 0.6) {
            const phaseProgress = (progress - 0.3) / 0.3;
            hdmiAnimation.logoScale = 1 - Math.pow(1 - phaseProgress, 3); // Ease-out
            hdmiAnimation.fadeProgress = 0;
        }
        // Phase 3: Fade in new input (60-100%)
        else {
            const phaseProgress = (progress - 0.6) / 0.4;
            hdmiAnimation.fadeProgress = phaseProgress;
            hdmiAnimation.logoScale = 1;
        }
        
        if (progress >= 1) {
            hdmiAnimation.isAnimating = false;
            hdmiAnimation.fadeProgress = 1;
            hdmiAnimation.logoScale = 1;
        }
        updateTVScreen(tvState);
    }
    
    // Channel overlay animation
    if (channelOverlay.visible) {
        const elapsed = Date.now() - channelOverlay.startTime;
        const progress = Math.min(elapsed / channelOverlay.duration, 1);
        
        if (progress < 0.2) {
            // Fade in and slide down
            const fadeProgress = progress / 0.2;
            channelOverlay.opacity = fadeProgress;
            channelOverlay.scale = 0.8 + (fadeProgress * 0.2);
            channelOverlay.slideY = -50 + (fadeProgress * 50);
        } else if (progress < 0.8) {
            // Visible
            channelOverlay.opacity = 1;
            channelOverlay.scale = 1;
            channelOverlay.slideY = 0;
        } else {
            // Fade out
            const fadeProgress = (progress - 0.8) / 0.2;
            channelOverlay.opacity = 1 - fadeProgress;
            channelOverlay.scale = 1 - (fadeProgress * 0.2);
            channelOverlay.slideY = fadeProgress * 50;
        }
        
        if (progress >= 1) {
            channelOverlay.visible = false;
        }
        updateTVScreen(tvState);
    }
    
    // Continuous screen updates during any animation
    if (powerAnimation.isAnimating || channelAnimation.isAnimating || 
        appAnimation.isAnimating || volumeAnimation.isAnimating ||
        hdmiAnimation.isAnimating || channelOverlay.visible) {
        updateTVScreen(tvState);
    }
    
    // Subtle TV glow effect when powered on (after animation)
    if (tvMesh && tvState.powered_on && !powerAnimation.isAnimating && screenMesh && screenMesh.material) {
        const time = Date.now() * 0.001;
        const glowIntensity = 0.05 + Math.sin(time * 2) * 0.03;
        // Maintain full brightness with subtle pulse
        screenMesh.material.emissiveIntensity = Math.min(1.0, 0.95 + glowIntensity);
        
        // Subtle bezel glow pulse
        if (tvFrame && tvFrame.material) {
            const bezelGlow = 0.08 + Math.sin(time * 1.5) * 0.02;
            tvFrame.material.emissiveIntensity = bezelGlow;
        }
        
        // TV ambient light breathing effect
        if (tvGlowLight) {
            const lightBreath = 0.8 + Math.sin(time * 1.2) * 0.1;
            tvGlowLight.intensity = lightBreath;
        }
    }
    
    // Animate button press feedback
    if (activeButton && Date.now() - buttonPressTime < 200) {
        const elapsed = Date.now() - buttonPressTime;
        const intensity = 1 - (elapsed / 200);
        activeButton.material.emissiveIntensity = intensity;
        activeButton.position.z = 0.03 - (intensity * 0.01);
    } else if (activeButton) {
        activeButton.material.emissive.setHex(0x000000);
        activeButton.material.emissiveIntensity = 0;
        activeButton.position.z = 0.03;
        activeButton = null;
    }
    
    // Animate remote control (subtle floating)
    if (remoteGroup) {
        const time = Date.now() * 0.001;
        remoteGroup.position.y = 0.8 + Math.sin(time) * 0.02;
        remoteGroup.rotation.y = -Math.PI / 4 + Math.sin(time * 0.5) * 0.05;
    }
    
    // Animate particles
    if (window.animateParticles) {
        window.animateParticles();
    }
    
    renderer.render(scene, camera);
}

// Add ambient effects for immersion
function addAmbientEffects() {
    // Add subtle particles/dust in the air
    const particleCount = 100;
    const particles = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    
    for (let i = 0; i < particleCount * 3; i += 3) {
        positions[i] = (Math.random() - 0.5) * 20;
        positions[i + 1] = Math.random() * 10;
        positions[i + 2] = (Math.random() - 0.5) * 20;
    }
    
    particles.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    
    const particleMaterial = new THREE.PointsMaterial({
        color: 0xffffff,
        size: 0.05,
        transparent: true,
        opacity: 0.3
    });
    
    const particleSystem = new THREE.Points(particles, particleMaterial);
    scene.add(particleSystem);
    
    // Animate particles
    function animateParticles() {
        const positions = particles.attributes.position.array;
        for (let i = 1; i < positions.length; i += 3) {
            positions[i] -= 0.01;
            if (positions[i] < 0) {
                positions[i] = 10;
            }
        }
        particles.attributes.position.needsUpdate = true;
    }
    
    window.animateParticles = animateParticles;
}

// Handle window resize
function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

// Initialize everything
window.addEventListener('DOMContentLoaded', () => {
    // Initialize scene first
    initScene();
    
    // Then initialize socket connection
    initSocket();
    
    // Initialize screen with default state after a short delay to ensure everything is loaded
    setTimeout(() => {
        if (screenMesh) {
            // Use default state if tvState is empty
            const defaultState = {
                powered_on: false,
                volume: 50,
                channel: 1,
                muted: false,
                current_app: 'Home',
                channel_input: ''
            };
            const initialState = Object.keys(tvState).length > 0 ? tvState : defaultState;
            updateTVScreen(initialState);
            console.log('Initial screen texture applied');
        } else {
            console.warn('Screen mesh not available for initial update');
        }
    }, 200);
});
