import { motion } from 'motion/react';
import { AssetPlaceholder } from '../../components/AssetPlaceholder.jsx';
import { HubSatellite } from '../../components/HubSatellite.jsx';
import { Sticker } from '../../components/Sticker.jsx';

export default function Ch1Step7() {
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
          <Sticker variant="sat-sm" bg="cream" style={{ borderRadius: 28, letterSpacing: '0.2em' }}>
            ⋯⋯
          </Sticker>
        </HubSatellite.Satellite>
        <HubSatellite.Satellite position="br">
          <motion.div
            initial={{ x: 40, y: 40, scale: 0.7, opacity: 0 }}
            animate={{ x: 0, y: 0, scale: 1, opacity: 1 }}
            transition={{ duration: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
          >
            <Sticker variant="sat-lg" bg="accent" textColor="cream" rotation={2}>
              沒手機·解數獨
            </Sticker>
          </motion.div>
        </HubSatellite.Satellite>
      </HubSatellite>
    </div>
  );
}
