
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
    let mouseDownPosition = { x: 0, y: 0 };
    let previousMousePosition = { x: 0, y: 0 };
    const DRAG_THRESHOLD_PX = 5;
    let cameraDistance = 5;
    let targetCameraPosition = new THREE.Vector3(0, 1.5, 5);
    let currentCameraPosition = targetCameraPosition.clone();
    let targetCameraLookAt = new THREE.Vector3(TV_POSITION.x, TV_POSITION.y, TV_POSITION.z);
    let currentCameraLookAt = targetCameraLookAt.clone();
    // Only these two + keydown below may set target* – no other code path (prevents bleed)
    const TV_CENTER = new THREE.Vector3(TV_POSITION.x, TV_POSITION.y, TV_POSITION.z);
    
    const canvas = renderer.domElement;
    
    // Mouse click for remote interaction
    canvas.addEventListener('click', (e) => {
        mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
        mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;
        
        raycaster.setFromCamera(mouse, camera);
        const intersects = raycaster.intersectObjects(remoteGroup.children, true);
        
        // Find first hit that belongs to a button (labels/overlays can block, so check all intersects)
        for (let i = 0; i < intersects.length; i++) {
            let obj = intersects[i].object;
            while (obj && obj.userData.buttonCode === undefined && obj.parent) {
                obj = obj.parent;
            }
            if (obj && obj.userData.buttonCode !== undefined) {
                const button = obj;
                // Visual feedback: highlight button immediately
                highlightRemoteButton(button.userData.buttonName);
                triggerIRSignal(button.userData.buttonName);
                if (socket && socket.connected) {
                    socket.emit('button_press', { button_code: button.userData.buttonCode });
                    console.log(`Clicked button: ${button.userData.buttonName} (0x${button.userData.buttonCode.toString(16).toUpperCase()})`);
                } else {
                    console.warn('WebSocket not connected, button press not sent to server');
                }
                return;
            }
        }
    });
    
    canvas.addEventListener('mousedown', (e) => {
        if (e.button !== 0) return; // only left button starts drag
        mouseDownPosition = { x: e.clientX, y: e.clientY };
        previousMousePosition = { x: e.clientX, y: e.clientY };
        isDragging = false; // will set true in mousemove once past threshold
    });
    
    canvas.addEventListener('mousemove', (e) => {
        // Walk mode: pointer lock look
        if (walkMode && document.pointerLockElement === canvas) {
            playerYaw += e.movementX * 0.002;
            playerPitch += e.movementY * 0.002;
            playerPitch = Math.max(-Math.PI / 2 + 0.15, Math.min(Math.PI / 2 - 0.15, playerPitch));
            return;
        }
        if (!isDragging) {
            const dx = e.clientX - mouseDownPosition.x;
            const dy = e.clientY - mouseDownPosition.y;
            if (dx * dx + dy * dy > DRAG_THRESHOLD_PX * DRAG_THRESHOLD_PX) {
                isDragging = true;
                canvas.style.cursor = 'grabbing';
            }
        }
        if (!isDragging) {
            // Check for button hover
            mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
            mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;
            raycaster.setFromCamera(mouse, camera);
            const intersects = raycaster.intersectObjects(remoteGroup.children, true);
            
            let overButton = false;
            for (let i = 0; i < intersects.length; i++) {
                let obj = intersects[i].object;
                while (obj && obj.userData.buttonCode === undefined && obj.parent) {
                    obj = obj.parent;
                }
                if (obj && obj.userData.buttonCode !== undefined) {
                    overButton = true;
                    break;
                }
            }
            canvas.style.cursor = overButton ? 'pointer' : 'grab';
            return;
        }
        
        if (!isDragging) return;
        const deltaX = e.clientX - previousMousePosition.x;
        const deltaY = e.clientY - previousMousePosition.y;
        // Use TARGET position for orbit (not lerped current) so orbit is stable and doesn't drift toward TV
        const orbitCenter = targetCameraLookAt.clone();
        cameraDistance = targetCameraPosition.distanceTo(orbitCenter);
        const spherical = new THREE.Spherical();
        spherical.setFromVector3(targetCameraPosition.clone().sub(orbitCenter));
        spherical.theta -= deltaX * 0.01;
        spherical.phi += deltaY * 0.01;
        spherical.phi = Math.max(0.1, Math.min(Math.PI - 0.1, spherical.phi));
        targetCameraPosition.copy(new THREE.Vector3().setFromSpherical(spherical).add(orbitCenter));
        targetCameraLookAt.copy(orbitCenter);
        previousMousePosition = { x: e.clientX, y: e.clientY };
    });
    
    canvas.addEventListener('mouseup', (e) => {
        if (e.button === 0) {
            isDragging = false;
            canvas.style.cursor = 'grab';
        }
    });
    
    canvas.style.cursor = 'grab';
    
    canvas.addEventListener('wheel', (e) => {
        e.preventDefault();
        cameraDistance += e.deltaY * 0.01;
        cameraDistance = Math.max(1.2, Math.min(15, cameraDistance));
        const center = targetCameraLookAt.clone();
        // Use target position for direction so zoom doesn't pull toward TV when current is still lerping
        const direction = targetCameraPosition.clone().sub(center).normalize();
        targetCameraPosition.copy(center).add(direction.multiplyScalar(cameraDistance));
    });
    
    // WASD keyup: clear movement flags (walk mode)
    window.addEventListener('keyup', (e) => {
        if (!walkMode) return;
        if (e.code === 'KeyW') moveForward = false;
        if (e.code === 'KeyS') moveBackward = false;
        if (e.code === 'KeyA') moveLeft = false;
        if (e.code === 'KeyD') moveRight = false;
    });

    // Only place (with the two buttons below) that set camera targets – no other logic may touch them
    window.addEventListener('keydown', (e) => {
        if (e.repeat) return; // ignore key hold so orbit/scroll don't get overwritten by repeated reset
        if (walkMode) {
            if (e.code === 'KeyW') { e.preventDefault(); moveForward = true; return; }
            if (e.code === 'KeyS') { e.preventDefault(); moveBackward = true; return; }
            if (e.code === 'KeyA') { e.preventDefault(); moveLeft = true; return; }
            if (e.code === 'KeyD') { e.preventDefault(); moveRight = true; return; }
            if (e.code === 'Escape') {
                e.preventDefault();
                document.exitPointerLock();
                return;
            }
        }
        if (e.code === 'Space') {
            e.preventDefault();
            firstPersonMode = false;
            if (armGroup) armGroup.visible = false;
            if (remoteGroup && firstPersonHolder && remoteGroup.parent === firstPersonHolder) {
                if (remoteGroup.parent) remoteGroup.parent.remove(remoteGroup);
                scene.add(remoteGroup);
                remoteGroup.position.copy(remoteLookClose.basePosition);
                remoteGroup.rotation.set(0, remoteLookClose.baseRotationY, 0);
                remoteGroup.scale.setScalar(remoteLookClose.baseScale);
            }
            targetCameraPosition.set(0, 1.5, 5);
            targetCameraLookAt.copy(TV_CENTER);
            snapCameraToTarget();
            document.getElementById('btn-zoom-tv')?.classList.remove('active');
            document.getElementById('btn-look-remote')?.classList.remove('active');
        } else if (e.code === 'Digit1') {
            firstPersonMode = false;
            if (armGroup) armGroup.visible = false;
            if (remoteGroup && firstPersonHolder && remoteGroup.parent === firstPersonHolder) {
                if (remoteGroup.parent) remoteGroup.parent.remove(remoteGroup);
                scene.add(remoteGroup);
                remoteGroup.position.copy(remoteLookClose.basePosition);
                remoteGroup.rotation.set(0, remoteLookClose.baseRotationY, 0);
                remoteGroup.scale.setScalar(remoteLookClose.baseScale);
            }
            targetCameraPosition.set(0, 1.5, 5);
            targetCameraLookAt.copy(TV_CENTER);
            snapCameraToTarget();
        } else if (e.code === 'Digit2') {
            firstPersonMode = false;
            if (armGroup) armGroup.visible = false;
            if (remoteGroup && firstPersonHolder && remoteGroup.parent === firstPersonHolder) {
                if (remoteGroup.parent) remoteGroup.parent.remove(remoteGroup);
                scene.add(remoteGroup);
                remoteGroup.position.copy(remoteLookClose.basePosition);
                remoteGroup.rotation.set(0, remoteLookClose.baseRotationY, 0);
                remoteGroup.scale.setScalar(remoteLookClose.baseScale);
            }
            targetCameraPosition.set(5, 1.5, 0);
            targetCameraLookAt.copy(TV_CENTER);
        } else if (e.code === 'Digit3') {
            firstPersonMode = false;
            if (armGroup) armGroup.visible = false;
            if (remoteGroup && firstPersonHolder && remoteGroup.parent === firstPersonHolder) {
                if (remoteGroup.parent) remoteGroup.parent.remove(remoteGroup);
                scene.add(remoteGroup);
                remoteGroup.position.copy(remoteLookClose.basePosition);
                remoteGroup.rotation.set(0, remoteLookClose.baseRotationY, 0);
                remoteGroup.scale.setScalar(remoteLookClose.baseScale);
            }
            targetCameraPosition.set(0, 8, 0);
            targetCameraLookAt.copy(TV_CENTER);
        } else if (e.code === 'Digit4') {
            if (typeof window.switchViewToRemote === 'function') window.switchViewToRemote();
        } else if (e.code === 'KeyP') {
            // P = Power (turn TV on/off) - works without clicking 3D remote
            e.preventDefault();
            if (socket && socket.connected) {
                socket.emit('button_press', { button_code: 0x10 });
                console.log('Keyboard: Power (P)');
            }
        } else if (e.code === 'KeyU') {
            // U = Volume Up
            e.preventDefault();
            if (socket && socket.connected) {
                socket.emit('button_press', { button_code: 0x11 });
            }
        } else if (e.code === 'KeyD') {
            // D = Volume Down (only if not ArrowDown to avoid conflict)
            if (!e.ctrlKey && !e.metaKey) {
                e.preventDefault();
                if (socket && socket.connected) {
                    socket.emit('button_press', { button_code: 0x12 });
                }
            }
        }
        // F1–F8: Room / Smart Home scenes and devices (0xE0–0xE7)
        if (e.code >= 'F1' && e.code <= 'F8' && !e.ctrlKey && !e.metaKey && !e.altKey) {
            const idx = parseInt(e.code.slice(1), 10) - 1;
            const code = 0xE0 + idx;
            e.preventDefault();
            if (socket && socket.connected) {
                socket.emit('button_press', { button_code: code });
            }
        }
        // Shift+F1–F8: House device toggles (0xE8–0xEF)
        if (e.shiftKey && e.code >= 'F1' && e.code <= 'F8' && !e.ctrlKey && !e.metaKey) {
            const idx = parseInt(e.code.slice(1), 10) - 1;
            const code = 0xE8 + idx;
            e.preventDefault();
            if (socket && socket.connected) {
                socket.emit('button_press', { button_code: code });
            }
        }
        // Ctrl+F1–F4: More house devices (0xF0–0xF3)
        if (e.ctrlKey && !e.metaKey && e.code >= 'F1' && e.code <= 'F4') {
            const idx = parseInt(e.code.slice(1), 10) - 1;
            const code = 0xF0 + idx;
            e.preventDefault();
            if (socket && socket.connected) {
                socket.emit('button_press', { button_code: code });
            }
        }
    });
    
    // Pointer lock: enter/exit walk mode
    document.addEventListener('pointerlockchange', () => {
        if (document.pointerLockElement === canvas) {
            walkMode = true;
            moveForward = moveBackward = moveLeft = moveRight = false;
            firstPersonMode = false;
            if (armGroup) armGroup.visible = false;
            if (remoteGroup && firstPersonHolder && remoteGroup.parent === firstPersonHolder) {
                if (remoteGroup.parent) remoteGroup.parent.remove(remoteGroup);
                scene.add(remoteGroup);
                remoteGroup.position.copy(remoteLookClose.basePosition);
                remoteGroup.rotation.set(0, remoteLookClose.baseRotationY, 0);
                remoteGroup.scale.setScalar(remoteLookClose.baseScale);
            }
            document.getElementById('btn-zoom-tv')?.classList.remove('active');
            document.getElementById('btn-look-remote')?.classList.remove('active');
            if (!playerPosition) playerPosition = new THREE.Vector3();
            playerPosition.copy(camera.position);
            playerPosition.y = EYE_HEIGHT;
            playerPosition.x = Math.max(-ROOM_BOUND, Math.min(ROOM_BOUND, playerPosition.x));
            playerPosition.z = Math.max(-ROOM_BOUND, Math.min(ROOM_BOUND, playerPosition.z));
            const forward = new THREE.Vector3(0, 0, -1).applyQuaternion(camera.quaternion);
            playerYaw = Math.atan2(forward.x, forward.z);
            playerPitch = Math.asin(Math.max(-1, Math.min(1, forward.y)));
            if (playerBody) playerBody.visible = true;
        } else {
            walkMode = false;
            moveForward = moveBackward = moveLeft = moveRight = false;
            if (playerBody) playerBody.visible = false;
            if (targetCameraPosition && currentCameraPosition) {
                targetCameraPosition.copy(camera.position);
                currentCameraPosition.copy(camera.position);
                targetCameraLookAt.copy(camera.position.clone().add(new THREE.Vector3(0, 0, -1).applyQuaternion(camera.quaternion)));
                currentCameraLookAt.copy(targetCameraLookAt);
                cameraDistance = camera.position.distanceTo(targetCameraLookAt);
            }
        }
    });

    // Smooth camera interpolation (position and lookAt); dt for walk mode movement
    function updateCamera(dt) {
        if (walkMode && playerPosition) {
            const move = (moveForward ? 1 : 0) - (moveBackward ? 1 : 0);
            const strafe = (moveRight ? 1 : 0) - (moveLeft ? 1 : 0);
            const rawDt = typeof dt === 'number' && dt > 0 ? dt : 0.016;
            const clampedDt = Math.min(rawDt, 0.1);
            const step = clampedDt * WALK_SPEED;
            if (move !== 0 || strafe !== 0) {
                const dx = Math.sin(playerYaw) * move + Math.cos(playerYaw) * strafe;
                const dz = Math.cos(playerYaw) * move - Math.sin(playerYaw) * strafe;
                const len = Math.sqrt(dx * dx + dz * dz);
                if (len > 0) {
                    playerPosition.x += (dx / len) * step;
                    playerPosition.z += (dz / len) * step;
                    playerPosition.x = Math.max(-ROOM_BOUND, Math.min(ROOM_BOUND, playerPosition.x));
                    playerPosition.z = Math.max(-ROOM_BOUND, Math.min(ROOM_BOUND, playerPosition.z));
                }
            }
            playerPosition.y = EYE_HEIGHT;
            camera.position.set(playerPosition.x, EYE_HEIGHT, playerPosition.z);
            const lookDir = new THREE.Vector3(
                Math.sin(playerYaw) * Math.cos(playerPitch),
                Math.sin(playerPitch),
                Math.cos(playerYaw) * Math.cos(playerPitch)
            );
            camera.lookAt(camera.position.clone().add(lookDir));
            return;
        }
        currentCameraPosition.lerp(targetCameraPosition, 0.1);
        currentCameraLookAt.lerp(targetCameraLookAt, 0.1);
        camera.position.copy(currentCameraPosition);
        camera.lookAt(currentCameraLookAt);
    }
    
    window.updateCamera = updateCamera;
    
    // Snap camera current to target so view switch doesn't lerp from old position (fixes broken POV)
    function snapCameraToTarget() {
        currentCameraPosition.copy(targetCameraPosition);
        currentCameraLookAt.copy(targetCameraLookAt);
        camera.position.copy(currentCameraPosition);
        camera.lookAt(currentCameraLookAt);
    }

    // Only these two + keydown above set target* – no camera orientation or other logic
    window.switchViewToTVZoom = function() {
        firstPersonMode = false;
        if (armGroup) armGroup.visible = false;
        if (remoteGroup && firstPersonHolder && remoteGroup.parent === firstPersonHolder) {
            if (remoteGroup.parent) remoteGroup.parent.remove(remoteGroup);
            scene.add(remoteGroup);
            remoteGroup.position.copy(remoteLookClose.basePosition);
            remoteGroup.rotation.set(0, remoteLookClose.baseRotationY, 0);
            remoteGroup.scale.setScalar(remoteLookClose.baseScale);
        }
        targetCameraPosition.set(0, 1.2, -5.6);
        targetCameraLookAt.copy(TV_CENTER);
        cameraDistance = 2.5;
        snapCameraToTarget();
        document.getElementById('btn-zoom-tv')?.classList.add('active');
        document.getElementById('btn-look-remote')?.classList.remove('active');
    };
    // Toggle: press once = lock into first-person (look at remote), press again = release to default view
    window.switchViewToRemote = function() {
        if (firstPersonMode) {
            // Already in first-person: release back to default TV view
            firstPersonMode = false;
            if (armGroup) armGroup.visible = false;
            if (remoteGroup && firstPersonHolder && remoteGroup.parent === firstPersonHolder) {
                if (remoteGroup.parent) remoteGroup.parent.remove(remoteGroup);
                scene.add(remoteGroup);
                remoteGroup.position.copy(remoteLookClose.basePosition);
                remoteGroup.rotation.set(0, remoteLookClose.baseRotationY, 0);
                remoteGroup.scale.setScalar(remoteLookClose.baseScale);
            }
            targetCameraPosition.set(0, 1.5, 5);
            targetCameraLookAt.copy(TV_CENTER);
            cameraDistance = 5;
            snapCameraToTarget();
            document.getElementById('btn-look-remote')?.classList.remove('active');
            return;
        }
        firstPersonMode = true;
        var r = remoteLookClose.basePosition;
        // First-person: eye position (slightly back and up), looking at the remote
        targetCameraPosition.set(r.x, r.y + 0.6, r.z + 1.5);
        targetCameraLookAt.set(r.x, r.y, r.z);
        cameraDistance = 1.8;
        // Attach remote+hand to holder that follows camera so they move with the viewer
        if (remoteGroup && firstPersonHolder) {
            if (remoteGroup.parent) remoteGroup.parent.remove(remoteGroup);
            remoteGroup.position.set(0, -0.35, -1.05);
            remoteGroup.rotation.set(0.25, 0, 0.05);
            remoteGroup.scale.setScalar(1);
            firstPersonHolder.add(remoteGroup);
        }
        snapCameraToTarget();
        document.getElementById('btn-zoom-tv')?.classList.remove('active');
        document.getElementById('btn-look-remote')?.classList.add('active');
    };
    // Enter first-person walk mode: pointer lock, WASD move, mouse look, visible body
    window.enterWalkMode = function() {
        canvas.requestPointerLock();
    };
}

// Update all room smart devices from TV state (remote-controlled: lights dim when TV on, ambient strip follows app)
