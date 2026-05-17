import { motion } from 'motion/react';
import { AssetPlaceholder } from '../../components/AssetPlaceholder.jsx';
import { HubSatellite } from '../../components/HubSatellite.jsx';
import { Sticker } from '../../components/Sticker.jsx';

export default function Ch1Step4() {
  return (
    <div style={{
      position: 'relative', zIndex: 20, height: '100%',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk',
    }}>
      <motion.div
        initial={{ y: -40, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.3, ease: 'easeOut' }}
        style={{
          position: 'absolute', top: 0, left: 0, right: 0,
          textAlign: 'center',
          fontWeight: 900, fontSize: '2rem', color: '#000',
        }}
      >
        靈感哪來呢？某天捷運上⋯
      </motion.div>

      <HubSatellite>
        <HubSatellite.Hub>
          <motion.div
            initial={{ scale: 0.85, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.4, delay: 0.7, ease: [0.34, 1.56, 0.64, 1] }}
          >
            <AssetPlaceholder type="[E]" width={960} height={540} todo="ch1 s4-s7 捷運窗景 SVG" />
          </motion.div>
        </HubSatellite.Hub>
        <HubSatellite.Satellite position="bl">
          <motion.div
            initial={{ x: -40, y: 40, scale: 0.7, opacity: 0 }}
            animate={{ x: 0, y: 0, scale: 1, opacity: 1 }}
            transition={{ duration: 0.5, delay: 1.0, ease: [0.34, 1.56, 0.64, 1] }}
          >
            <Sticker variant="sat-lg" bg="secondary" rotation={-4} style={{ borderRadius: 20 }}>
              正妹發呆中
            </Sticker>
          </motion.div>
        </HubSatellite.Satellite>
      </HubSatellite>
    </div>
  );
}
