import { motion } from 'motion/react';
import { AssetPlaceholder } from '../../components/AssetPlaceholder.jsx';
import { HubSatellite } from '../../components/HubSatellite.jsx';
import { Sticker } from '../../components/Sticker.jsx';

export default function Ch1Step6() {
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
          <Sticker variant="sat-lg" bg="muted" rotation={3}>
            Code Bullet
            <div style={{ fontSize: 16, marginTop: 4, fontWeight: 700 }}>· flappy bird</div>
          </Sticker>
        </HubSatellite.Satellite>
        <HubSatellite.Satellite position="tl">
          <motion.div
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: [0, 1, 1], opacity: 1 }}
            transition={{
              scale: { duration: 0.3, ease: [0.34, 1.56, 0.64, 1] },
              opacity: { duration: 0.3 },
            }}
          >
            <motion.div
              animate={{ scale: [1, 1.08, 1] }}
              transition={{ duration: 1, ease: 'easeInOut', repeat: Infinity }}
            >
              <Sticker variant="sat-sm" bg="cream" style={{ borderRadius: 28, letterSpacing: '0.2em' }}>
                ⋯⋯
              </Sticker>
            </motion.div>
          </motion.div>
        </HubSatellite.Satellite>
      </HubSatellite>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.4 }}
        style={{
          position: 'absolute', bottom: 0, right: 0,
          fontSize: 18, fontWeight: 700, color: '#666',
        }}
      >
        然後我繼續發呆⋯
      </motion.div>
    </div>
  );
}
