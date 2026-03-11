// Tawiza network — territorial data flows visualization
(function () {
    const canvas = document.getElementById('network-bg');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    let w, h, nodes, pulses, mouse;
    const NODE_COUNT = 100;
    const CONNECT_DIST = 180;
    const MOUSE_DIST = 280;
    const PULSE_CHANCE = 0.015;
    let time = 0;

    function resize() {
        w = canvas.width = window.innerWidth;
        h = canvas.height = window.innerHeight;
    }

    function createNodes() {
        nodes = [];
        for (let i = 0; i < NODE_COUNT; i++) {
            nodes.push({
                x: Math.random() * w,
                y: Math.random() * h,
                vx: (Math.random() - 0.5) * 0.5,
                vy: (Math.random() - 0.5) * 0.5,
                r: Math.random() * 2.5 + 1.5,
                phase: Math.random() * Math.PI * 2,
                hub: Math.random() < 0.12, // 12% are "hub" nodes — data sources
            });
        }
        pulses = [];
    }

    mouse = { x: -1000, y: -1000 };

    function spawnPulse(fromIdx, toIdx) {
        pulses.push({
            from: fromIdx,
            to: toIdx,
            t: 0,
            speed: 0.008 + Math.random() * 0.012,
        });
    }

    function draw() {
        ctx.clearRect(0, 0, w, h);
        time += 0.006;

        // Update positions
        for (const n of nodes) {
            n.x += n.vx;
            n.y += n.vy;
            if (n.x < -20) n.x = w + 20;
            if (n.x > w + 20) n.x = -20;
            if (n.y < -20) n.y = h + 20;
            if (n.y > h + 20) n.y = -20;
        }

        // Build connections list & draw them
        const connections = [];
        for (let i = 0; i < nodes.length; i++) {
            for (let j = i + 1; j < nodes.length; j++) {
                const dx = nodes[i].x - nodes[j].x;
                const dy = nodes[i].y - nodes[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < CONNECT_DIST) {
                    const alpha = (1 - dist / CONNECT_DIST);
                    connections.push([i, j, alpha, dist]);

                    // Draw connection line
                    ctx.beginPath();
                    ctx.moveTo(nodes[i].x, nodes[i].y);
                    ctx.lineTo(nodes[j].x, nodes[j].y);
                    ctx.strokeStyle = `rgba(217, 119, 6, ${alpha * 0.35})`;
                    ctx.lineWidth = alpha > 0.6 ? 1.2 : 0.7;
                    ctx.stroke();

                    // Randomly spawn data pulses on connections
                    if (Math.random() < PULSE_CHANCE && pulses.length < 30) {
                        spawnPulse(i, j);
                    }
                }
            }
        }

        // Draw & update data pulses (traveling dots along connections)
        for (let p = pulses.length - 1; p >= 0; p--) {
            const pulse = pulses[p];
            pulse.t += pulse.speed;
            if (pulse.t > 1) { pulses.splice(p, 1); continue; }

            const a = nodes[pulse.from];
            const b = nodes[pulse.to];
            const px = a.x + (b.x - a.x) * pulse.t;
            const py = a.y + (b.y - a.y) * pulse.t;
            const glow = Math.sin(pulse.t * Math.PI); // fade in/out

            // Pulse glow
            ctx.beginPath();
            ctx.arc(px, py, 5, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(245, 158, 11, ${glow * 0.2})`;
            ctx.fill();

            // Pulse core
            ctx.beginPath();
            ctx.arc(px, py, 2, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(245, 158, 11, ${glow * 0.8})`;
            ctx.fill();
        }

        // Draw nodes
        for (const n of nodes) {
            const dx = n.x - mouse.x;
            const dy = n.y - mouse.y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            const mouseGlow = dist < MOUSE_DIST ? 1 - dist / MOUSE_DIST : 0;
            const pulse = Math.sin(time * 3 + n.phase) * 0.25 + 0.75;
            const r = n.r * pulse + mouseGlow * 3;

            // Hub nodes get extra glow (represent data sources like INSEE, SIRENE...)
            if (n.hub) {
                ctx.beginPath();
                ctx.arc(n.x, n.y, r + 8, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(217, 119, 6, ${0.04 + Math.sin(time * 2 + n.phase) * 0.02})`;
                ctx.fill();

                ctx.beginPath();
                ctx.arc(n.x, n.y, r + 3, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(217, 119, 6, ${0.08})`;
                ctx.fill();
            }

            // Mouse proximity glow
            if (mouseGlow > 0.2) {
                ctx.beginPath();
                ctx.arc(n.x, n.y, r + 6, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(245, 158, 11, ${mouseGlow * 0.1})`;
                ctx.fill();
            }

            // Node core
            ctx.beginPath();
            ctx.arc(n.x, n.y, r, 0, Math.PI * 2);
            const baseAlpha = n.hub ? 0.7 : 0.4;
            ctx.fillStyle = `rgba(217, 119, 6, ${baseAlpha + mouseGlow * 0.5})`;
            ctx.fill();
        }

        // Mouse connections — data attraction effect
        for (const n of nodes) {
            const dx = n.x - mouse.x;
            const dy = n.y - mouse.y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            if (dist < MOUSE_DIST) {
                const alpha = (1 - dist / MOUSE_DIST);
                ctx.beginPath();
                ctx.moveTo(mouse.x, mouse.y);
                ctx.lineTo(n.x, n.y);
                ctx.strokeStyle = `rgba(245, 158, 11, ${alpha * 0.3})`;
                ctx.lineWidth = alpha > 0.5 ? 1 : 0.5;
                ctx.stroke();
            }
        }

        requestAnimationFrame(draw);
    }

    window.addEventListener('resize', () => { resize(); createNodes(); });
    window.addEventListener('mousemove', (e) => { mouse.x = e.clientX; mouse.y = e.clientY; });
    window.addEventListener('mouseleave', () => { mouse.x = -1000; mouse.y = -1000; });

    resize();
    createNodes();
    draw();
})();
