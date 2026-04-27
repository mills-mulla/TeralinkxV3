<template>
  <canvas ref="canvas" class="absolute inset-0 w-full h-full cursor-grab active:cursor-grabbing"></canvas>
</template>

<script>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import * as THREE from 'three'

export default {
  name: 'GlobeBackground',
  setup() {
    const canvas = ref(null)
    let renderer, scene, camera, animId, clock
    let globeGroup, atmosphere, satellites = [], pulses = [], locationDots = []
    let isDragging = false, prevMouse = { x: 0, y: 0 }
    let rotVel = { x: 0, y: 0.0008 }
    let autoRotate = true

    const RADIUS = 1.0

    const locations = [
      { name: 'Nairobi',   lat: -1.28,  lon: 36.82, hub: true  },
      { name: 'Mombasa',  lat: -4.05,  lon: 39.67, hub: false },
      { name: 'Kisumu',   lat: -0.09,  lon: 34.76, hub: false },
      { name: 'Nakuru',   lat: -0.30,  lon: 36.07, hub: false },
      { name: 'Eldoret',  lat:  0.52,  lon: 35.27, hub: false },
      { name: 'London',   lat: 51.50,  lon: -0.12, hub: true  },
      { name: 'Dubai',    lat: 25.20,  lon: 55.27, hub: false },
      { name: 'Mumbai',   lat: 19.07,  lon: 72.87, hub: false },
      { name: 'New York', lat: 40.71,  lon: -74.0, hub: true  },
      { name: 'Tokyo',    lat: 35.68,  lon: 139.7, hub: false },
      { name: 'Sydney',   lat: -33.87, lon: 151.2, hub: false },
      { name: 'Lagos',    lat:  6.52,  lon:  3.38, hub: false },
    ]

    // Continent outline points (simplified lat/lon pairs)
    const continentPoints = [
      // Africa
      ...generateContinent([
        [37,-5],[35,10],[30,20],[15,30],[5,35],[-5,40],[-20,35],[-30,25],[-35,20],[-30,15],[-20,10],[-10,5],[0,0],[10,-5],[20,-10],[30,-5],[37,-5]
      ]),
      // Europe
      ...generateContinent([
        [70,20],[65,30],[60,25],[55,20],[50,15],[45,10],[40,5],[45,0],[50,-5],[55,0],[60,5],[65,10],[70,15],[70,20]
      ]),
      // Asia
      ...generateContinent([
        [70,60],[65,80],[60,100],[55,120],[50,130],[40,140],[30,120],[20,110],[10,100],[0,100],[10,80],[20,70],[30,60],[40,50],[50,40],[60,50],[70,60]
      ]),
      // North America
      ...generateContinent([
        [70,-140],[65,-120],[60,-100],[55,-80],[50,-70],[45,-60],[40,-70],[35,-80],[30,-90],[25,-80],[20,-90],[25,-100],[30,-110],[40,-120],[50,-130],[60,-140],[70,-140]
      ]),
      // South America
      ...generateContinent([
        [10,-70],[5,-60],[0,-50],[-10,-40],[-20,-45],[-30,-50],[-40,-65],[-50,-70],[-55,-65],[-50,-60],[-40,-55],[-30,-45],[-20,-40],[-10,-50],[0,-60],[10,-70]
      ]),
      // Australia
      ...generateContinent([
        [-15,130],[-20,140],[-25,150],[-30,145],[-35,140],[-38,145],[-35,150],[-30,155],[-25,150],[-20,145],[-15,140],[-10,135],[-15,130]
      ]),
    ]

    function generateContinent(points) {
      const result = []
      for (let i = 0; i < points.length - 1; i++) {
        const steps = 8
        for (let s = 0; s <= steps; s++) {
          const t = s / steps
          const lat = points[i][0] + (points[i+1][0] - points[i][0]) * t
          const lon = points[i][1] + (points[i+1][1] - points[i][1]) * t
          result.push([lat, lon])
        }
      }
      return result
    }

    const latLonToVec3 = (lat, lon, r) => {
      const phi   = (90 - lat) * (Math.PI / 180)
      const theta = (lon + 180) * (Math.PI / 180)
      return new THREE.Vector3(
        -r * Math.sin(phi) * Math.cos(theta),
         r * Math.cos(phi),
         r * Math.sin(phi) * Math.sin(theta)
      )
    }

    const init = () => {
      const w = canvas.value.clientWidth
      const h = canvas.value.clientHeight

      clock = new THREE.Clock()

      renderer = new THREE.WebGLRenderer({ canvas: canvas.value, antialias: true, alpha: true })
      renderer.setSize(w, h)
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
      renderer.setClearColor(0x000000, 0)

      scene = new THREE.Scene()

      // Camera offset left so globe sits left-center
      camera = new THREE.PerspectiveCamera(42, w / h, 0.1, 1000)
      camera.position.set(-0.4, 0.1, 2.8)
      camera.lookAt(-0.2, 0, 0)

      // Lights
      scene.add(new THREE.AmbientLight(0x223355, 3))
      const sun = new THREE.DirectionalLight(0x4488ff, 4)
      sun.position.set(4, 2, 4)
      scene.add(sun)
      const rim = new THREE.DirectionalLight(0x00ccff, 1.5)
      rim.position.set(-4, -1, -2)
      scene.add(rim)

      // Globe group (everything rotates together)
      globeGroup = new THREE.Group()
      globeGroup.position.set(-0.2, 0, 0)
      scene.add(globeGroup)

      // Globe base — dark ocean
      const globeGeo = new THREE.SphereGeometry(RADIUS, 64, 64)
      const globeMat = new THREE.MeshPhongMaterial({
        color: 0x050d1f,
        emissive: 0x050d1f,
        specular: 0x1144aa,
        shininess: 60,
      })
      globeGroup.add(new THREE.Mesh(globeGeo, globeMat))

      // Lat/lon grid lines
      const gridMat = new THREE.LineBasicMaterial({ color: 0x0d2040, transparent: true, opacity: 0.5 })
      for (let lat = -80; lat <= 80; lat += 20) {
        const pts = []
        for (let lon = 0; lon <= 360; lon += 4) pts.push(latLonToVec3(lat, lon - 180, RADIUS + 0.001))
        globeGroup.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), gridMat))
      }
      for (let lon = 0; lon < 360; lon += 20) {
        const pts = []
        for (let lat = -90; lat <= 90; lat += 4) pts.push(latLonToVec3(lat, lon - 180, RADIUS + 0.001))
        globeGroup.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), gridMat))
      }

      // Continent dot cloud
      const contMat = new THREE.PointsMaterial({ color: 0x1a6aaa, size: 0.008, transparent: true, opacity: 0.7 })
      const contPositions = []
      continentPoints.forEach(([lat, lon]) => {
        const v = latLonToVec3(lat, lon, RADIUS + 0.002)
        contPositions.push(v.x, v.y, v.z)
      })
      const contGeo = new THREE.BufferGeometry()
      contGeo.setAttribute('position', new THREE.Float32BufferAttribute(contPositions, 3))
      globeGroup.add(new THREE.Points(contGeo, contMat))

      // Atmosphere glow
      const atmMat = new THREE.MeshPhongMaterial({ color: 0x0055ff, transparent: true, opacity: 0.06, side: THREE.BackSide })
      atmosphere = new THREE.Mesh(new THREE.SphereGeometry(RADIUS * 1.12, 64, 64), atmMat)
      globeGroup.add(atmosphere)

      // Atmosphere rim
      const rimMat = new THREE.MeshPhongMaterial({ color: 0x0088ff, transparent: true, opacity: 0.12, side: THREE.BackSide })
      globeGroup.add(new THREE.Mesh(new THREE.SphereGeometry(RADIUS * 1.06, 64, 64), rimMat))

      // Location dots + rings
      locations.forEach((loc, i) => {
        const pos = latLonToVec3(loc.lat, loc.lon, RADIUS + 0.005)
        const color = loc.hub ? 0x00ffcc : 0x0088ff
        const size = loc.hub ? 0.018 : 0.011

        const dot = new THREE.Mesh(
          new THREE.SphereGeometry(size, 8, 8),
          new THREE.MeshBasicMaterial({ color })
        )
        dot.position.copy(pos)
        globeGroup.add(dot)

        // Pulse ring
        const ring = new THREE.Mesh(
          new THREE.RingGeometry(size * 1.5, size * 2, 32),
          new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.8, side: THREE.DoubleSide })
        )
        ring.position.copy(pos)
        ring.lookAt(new THREE.Vector3(0, 0, 0))
        ring.userData = { phase: (i / locations.length) * Math.PI * 2, pos: pos.clone() }
        globeGroup.add(ring)
        locationDots.push({ dot, ring, pos: pos.clone() })
      })

      // Satellites
      const satDefs = [
        { radius: 1.45, speed: 0.45, tiltX: 0.4,  tiltY: 0.0,  color: 0x00ffcc, startAngle: 0 },
        { radius: 1.55, speed: 0.32, tiltX: 1.2,  tiltY: 0.8,  color: 0x4488ff, startAngle: 2.1 },
        { radius: 1.38, speed: 0.55, tiltX: 0.8,  tiltY: 2.0,  color: 0xff6644, startAngle: 4.2 },
        { radius: 1.62, speed: 0.28, tiltX: 1.6,  tiltY: 1.2,  color: 0xffcc00, startAngle: 1.0 },
      ]

      satDefs.forEach(def => {
        // Orbit path
        const orbitPts = []
        for (let a = 0; a <= Math.PI * 2; a += 0.05) {
          const p = new THREE.Vector3(Math.cos(a) * def.radius, 0, Math.sin(a) * def.radius)
          p.applyEuler(new THREE.Euler(def.tiltX, def.tiltY, 0))
          orbitPts.push(p)
        }
        const orbitLine = new THREE.Line(
          new THREE.BufferGeometry().setFromPoints(orbitPts),
          new THREE.LineBasicMaterial({ color: 0x1a3355, transparent: true, opacity: 0.35 })
        )
        scene.add(orbitLine)

        // Satellite body
        const body = new THREE.Mesh(
          new THREE.BoxGeometry(0.045, 0.018, 0.018),
          new THREE.MeshPhongMaterial({ color: def.color, emissive: def.color, emissiveIntensity: 0.6 })
        )
        // Solar panels
        const panelMat = new THREE.MeshPhongMaterial({ color: 0x1155cc, emissive: 0x001144, emissiveIntensity: 0.3 })
        ;[-1, 1].forEach(side => {
          const panel = new THREE.Mesh(new THREE.BoxGeometry(0.055, 0.003, 0.028), panelMat)
          panel.position.set(side * 0.05, 0, 0)
          body.add(panel)
        })
        // Antenna
        const ant = new THREE.Mesh(
          new THREE.CylinderGeometry(0.001, 0.001, 0.025, 4),
          new THREE.MeshBasicMaterial({ color: def.color })
        )
        ant.position.set(0, 0.02, 0)
        body.add(ant)

        // Dish
        const dish = new THREE.Mesh(
          new THREE.ConeGeometry(0.008, 0.012, 8, 1, true),
          new THREE.MeshBasicMaterial({ color: def.color, side: THREE.DoubleSide, transparent: true, opacity: 0.8 })
        )
        dish.position.set(0, -0.015, 0)
        dish.rotation.x = Math.PI
        body.add(dish)

        scene.add(body)
        satellites.push({ body, ...def, angle: def.startAngle, pulseTimer: 0, pulseInterval: 1.5 + Math.random() * 2 })
      })

      // Signal pulse pool
      for (let i = 0; i < 12; i++) {
        const geo = new THREE.BufferGeometry().setFromPoints(Array(30).fill(new THREE.Vector3()))
        const mat = new THREE.LineBasicMaterial({ color: 0x00ffcc, transparent: true, opacity: 0 })
        const line = new THREE.Line(geo, mat)
        scene.add(line)
        pulses.push({ line, active: false, progress: 0, from: null, to: null, color: 0x00ffcc })
      }

      setupMouseEvents()
      animate()
    }

    const spawnPulse = (from, to, color) => {
      const p = pulses.find(p => !p.active)
      if (!p) return
      p.active = true; p.progress = 0
      p.from = from.clone(); p.to = to.clone()
      p.line.material.color.setHex(color)
    }

    const updatePulse = (p, dt) => {
      if (!p.active) return
      p.progress += dt * 0.45
      if (p.progress >= 1) { p.active = false; p.line.material.opacity = 0; return }
      const pts = []
      const mid = p.from.clone().add(p.to).multiplyScalar(0.5).normalize().multiplyScalar(1.8)
      for (let i = 0; i <= 29; i++) {
        const t = (i / 29) * p.progress
        const a = p.from.clone().multiplyScalar((1-t)*(1-t))
        const b = mid.clone().multiplyScalar(2*(1-t)*t)
        const c = p.to.clone().multiplyScalar(t*t)
        pts.push(a.add(b).add(c))
      }
      p.line.geometry.setFromPoints(pts)
      p.line.material.opacity = 0.85 * Math.sin(p.progress * Math.PI)
    }

    const animate = () => {
      animId = requestAnimationFrame(animate)
      const dt = Math.min(clock.getDelta(), 0.05)
      const t = clock.getElapsedTime()

      // Auto rotate with inertia
      if (!isDragging) {
        rotVel.y += (0.0008 - rotVel.y) * 0.02
        rotVel.x += (0 - rotVel.x) * 0.05
      }
      globeGroup.rotation.y += rotVel.y
      globeGroup.rotation.x += rotVel.x
      globeGroup.rotation.x = Math.max(-0.5, Math.min(0.5, globeGroup.rotation.x))

      // Pulse rings
      locationDots.forEach(({ ring }, i) => {
        const s = 1 + 0.6 * Math.abs(Math.sin(t * 1.2 + ring.userData.phase))
        ring.scale.setScalar(s)
        ring.material.opacity = 0.7 * (1 - (s - 1) / 0.6)
      })

      // Orbit satellites
      satellites.forEach(s => {
        s.angle += s.speed * dt
        const pos = new THREE.Vector3(Math.cos(s.angle) * s.radius, 0, Math.sin(s.angle) * s.radius)
        pos.applyEuler(new THREE.Euler(s.tiltX, s.tiltY, 0))
        s.body.position.copy(pos)
        s.body.lookAt(new THREE.Vector3(0, 0, 0))
        s.body.rotateX(Math.PI / 2)

        s.pulseTimer += dt
        if (s.pulseTimer >= s.pulseInterval) {
          s.pulseTimer = 0
          const loc = locations[Math.floor(Math.random() * locations.length)]
          const target = latLonToVec3(loc.lat, loc.lon, RADIUS)
          // Transform target to world space
          const worldTarget = target.clone().applyEuler(globeGroup.rotation).add(globeGroup.position)
          spawnPulse(pos, worldTarget, s.color)
        }
      })

      pulses.forEach(p => updatePulse(p, dt))
      renderer.render(scene, camera)
    }

    // Mouse / touch drag
    const setupMouseEvents = () => {
      const el = canvas.value

      const onDown = (x, y) => {
        isDragging = true
        prevMouse = { x, y }
        rotVel = { x: 0, y: 0 }
      }
      const onMove = (x, y) => {
        if (!isDragging) return
        const dx = x - prevMouse.x
        const dy = y - prevMouse.y
        rotVel.y = dx * 0.005
        rotVel.x = dy * 0.005
        globeGroup.rotation.y += rotVel.y
        globeGroup.rotation.x += rotVel.x
        globeGroup.rotation.x = Math.max(-0.5, Math.min(0.5, globeGroup.rotation.x))
        prevMouse = { x, y }
      }
      const onUp = () => { isDragging = false }

      el.addEventListener('mousedown', e => onDown(e.clientX, e.clientY))
      el.addEventListener('mousemove', e => onMove(e.clientX, e.clientY))
      el.addEventListener('mouseup', onUp)
      el.addEventListener('mouseleave', onUp)
      el.addEventListener('touchstart', e => onDown(e.touches[0].clientX, e.touches[0].clientY), { passive: true })
      el.addEventListener('touchmove', e => onMove(e.touches[0].clientX, e.touches[0].clientY), { passive: true })
      el.addEventListener('touchend', onUp)
    }

    const onResize = () => {
      if (!canvas.value || !renderer) return
      const w = canvas.value.clientWidth
      const h = canvas.value.clientHeight
      camera.aspect = w / h
      camera.updateProjectionMatrix()
      renderer.setSize(w, h)
    }

    onMounted(() => { init(); window.addEventListener('resize', onResize) })
    onBeforeUnmount(() => { cancelAnimationFrame(animId); renderer?.dispose(); window.removeEventListener('resize', onResize) })

    return { canvas }
  }
}
</script>
