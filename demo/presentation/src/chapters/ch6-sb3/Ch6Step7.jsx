import { motion } from 'motion/react';
import { RedStamp } from '../../motifs/RedStamp.jsx';

export default function Ch6Step7() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32,
    }}>
      <div style={{ position: 'absolute', top: 64, left: 64 }}>
        <RedStamp active rotation={-8} size="medium">偷吃步</RedStamp>
      </div>

      <motion.div
        initial={{ clipPath: 'inset(0px 100% 0px 0px)', opacity: 0 }}
        animate={{ clipPath: 'inset(-24px)', opacity: 1 }}
        transition={{ duration: 0.8, delay: 0.3, ease: 'easeOut' }}
        style={{
          fontWeight: 900, fontSize: '3rem', textAlign: 'center', lineHeight: 1.5, maxWidth: 1200,
        }}
      >
        <span style={{ background: '#FF6B6B', color: '#FFF', padding: '4px 16px', border: '4px solid #000' }}>
          計分標準太簡單了
        </span>
        <br/>
        <span style={{ background: '#FFD93D', color: '#000', padding: '4px 16px', border: '4px solid #000', marginTop: 16, display: 'inline-block' }}>
          AI 就會找漏洞作弊
        </span>
      </motion.div>
    </main>
  );
}
