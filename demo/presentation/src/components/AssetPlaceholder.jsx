export function AssetPlaceholder({ type = '[E]', width = 600, height = 360, todo = 'asset TODO' }) {
  return (
    <div
      role="img"
      aria-label={`TODO: ${todo}`}
      style={{
        width, height,
        background: '#FFFDF5',
        border: '4px dashed #FF6B6B',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        flexDirection: 'column', padding: 16, textAlign: 'center',
        fontFamily: 'Space Grotesk', fontWeight: 700, color: '#FF6B6B',
      }}
    >
      <div style={{ fontSize: 14, marginBottom: 8 }}>{type}</div>
      <div style={{ fontSize: 18 }}>⚠️ TODO</div>
      <div style={{ fontSize: 14, marginTop: 8, color: '#000' }}>{todo}</div>
    </div>
  );
}
