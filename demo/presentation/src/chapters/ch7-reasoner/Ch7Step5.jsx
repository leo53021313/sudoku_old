import { motion } from 'motion/react';
import { SudokuBoardLive } from '../../motifs/SudokuBoardLive.jsx';

const BOARD = [
  [5,3,4, 6,7,8, 9,1,2],
  [6,7,0, 1,9,5, 3,4,8],
  [1,9,8, 3,4,2, 5,6,7],
  [8,5,9, 7,6,1, 4,2,3],
  [4,2,6, 8,5,3, 7,9,1],
  [7,1,3, 9,2,4, 8,5,6],
  [9,6,1, 5,3,7, 2,8,4],
  [2,8,7, 4,1,9, 6,3,5],
  [3,4,5, 2,8,6, 1,7,9],
];
const HIGHLIGHTS = [[1, 2]];

export default function Ch7Step5() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32, gap: 24,
    }}>
      <motion.div
        initial={{ y: -40, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.4 }}
        style={{ fontWeight: 900, fontSize: '3rem', textAlign: 'center' }}
      >
        多了一倍可以做的事
      </motion.div>

      <SudokuBoardLive cells={BOARD} highlights={HIGHLIGHTS} active />

      <div style={{ display: 'flex', gap: 32, fontWeight: 900, fontSize: 20 }}>
        <span style={{
          background: '#10B981', color: '#FFF',
          padding: '12px 24px', border: '4px solid #000', boxShadow: '6px 6px 0 0 #000',
        }}>填一個數字</span>
        <span style={{
          background: '#FF6B6B', color: '#FFF',
          padding: '12px 24px', border: '4px solid #000', boxShadow: '6px 6px 0 0 #000',
        }}>劃掉這格不可能是這個數 ✗</span>
      </div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 1.0 }}
        style={{ fontWeight: 700, fontSize: '1.25rem', color: '#666', marginTop: 8 }}
      >
        消去類技巧才能展示出來
      </motion.div>
    </main>
  );
}
