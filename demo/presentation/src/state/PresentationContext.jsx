import { createContext, useContext, useState } from 'react';
import { usePresentation } from './usePresentation.js';
import { useUrlSync, parseUrl } from './useUrlSync.js';
import { useKeyMouseControls } from './useKeyMouseControls.js';

const Ctx = createContext(null);

export function PresentationProvider({ children }) {
  const initial = parseUrl(window.location.href);
  const pres = usePresentation(initial);
  const [presenter, setPresenter] = useState(initial.presenter);
  const [progressVisible, setProgressVisible] = useState(false);

  useUrlSync(pres, presenter);
  useKeyMouseControls({
    advance: pres.advance,
    retreat: pres.retreat,
    toggleProgress: () => setProgressVisible(v => !v),
  });

  return (
    <Ctx.Provider value={{ ...pres, presenter, setPresenter, progressVisible, setProgressVisible }}>
      {children}
    </Ctx.Provider>
  );
}

export function usePresentationContext() {
  const c = useContext(Ctx);
  if (!c) throw new Error('usePresentationContext must be used inside PresentationProvider');
  return c;
}
