import { createContext, useContext, useRef, useState } from 'react';
import { usePresentation } from './usePresentation.js';
import { useUrlSync, parseUrl } from './useUrlSync.js';
import { useKeyMouseControls } from './useKeyMouseControls.js';

const Ctx = createContext(null);

export function PresentationProvider({ children }) {
  const initial = parseUrl(window.location.href);
  const pres = usePresentation(initial);
  const [presenter, setPresenter] = useState(initial.presenter);
  const [progressVisible, setProgressVisible] = useState(false);

  // Shared shake controller — ScreenShake (mounted in App.jsx) attaches its imperative
  // handle to this ref. Any chapter step can call triggerShake() via context.
  const shakeRef = useRef(null);
  const triggerShake = () => shakeRef.current?.play();

  useUrlSync(pres, presenter);
  useKeyMouseControls({
    advance: pres.advance,
    retreat: pres.retreat,
    toggleProgress: () => setProgressVisible(v => !v),
  });

  return (
    <Ctx.Provider value={{
      ...pres,
      presenter, setPresenter,
      progressVisible, setProgressVisible,
      shakeRef,
      triggerShake,
    }}>
      {children}
    </Ctx.Provider>
  );
}

export function usePresentationContext() {
  const c = useContext(Ctx);
  if (!c) throw new Error('usePresentationContext must be used inside PresentationProvider');
  return c;
}
