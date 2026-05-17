import { motion } from 'motion/react';
import { AssetPlaceholder } from '../../components/AssetPlaceholder.jsx';
import { HubSatellite } from '../../components/HubSatellite.jsx';
import { Sticker } from '../../components/Sticker.jsx';

export default function Ch1Step5() {
  return (
    <div style={{
      position: 'relative', zIndex: 20, height: '100%',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk',
    }}>
      <HubSatellite>
        <HubSatellite.Hub>
          <AssetPlaceholder type="[E]" width={960} height={540} todo="ch1 s4-s7 捷運窗景 SVG" />
        </HubSatellite.Hub>
        <HubSatellite.Satellite position="bl">
          <Sticker variant="sat-lg" bg="secondary" rotation={-4} style={{ borderRadius: 20 }}>
            正妹發呆中
          </Sticker>
        </HubSatellite.Satellite>
        <HubSatellite.Satellite position="tr">
          <motion.div
            initial={{ x: 40, y: -40, scale: 0.7, opacity: 0 }}
            animate={{ x: 0, y: 0, scale: 1, opacity: 1 }}
            transition={{ duration: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
          >
            <Sticker variant="sat-lg" bg="muted" rotation={3}>
              Code Bullet
              <div style={{ fontSize: 16, marginTop: 4, fontWeight: 700 }}>· flappy bird</div>
            </Sticker>
          </motion.div>
        </HubSatellite.Satellite>
      </HubSatellite>

      {/* Thought-bubble dashed arc (decoration overlay — full SafeArea) */}
      <svg
        viewBox="0 0 100 100"
        preserveAspectRatio="none"
        style={{
          position: 'absolute', inset: 0,
          width: '100%', height: '100%',
          pointerEvents: 'none', zIndex: 4,
        }}
      >
        <motion.path
          d="M 18 78 Q 50 30, 82 18"
          fill="none" stroke="#000"
          strokeWidth="2" strokeDasharray="6 6"
          vectorEffect="non-scaling-stroke"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 0.6, delay: 0.5, ease: 'easeOut' }}
        />
      </svg>
    </div>
  );
}
