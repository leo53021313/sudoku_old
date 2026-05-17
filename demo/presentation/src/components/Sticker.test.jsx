import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { Sticker, STICKER_VARIANTS } from './Sticker.jsx';

describe('<Sticker variant>', () => {
  it('exports a variant table with hub-md/hub-lg/hub-mega/sat-lg/sat-md/sat-sm/kicker keys', () => {
    expect(Object.keys(STICKER_VARIANTS).sort()).toEqual(
      ['hub-lg', 'hub-md', 'hub-mega', 'kicker', 'sat-lg', 'sat-md', 'sat-sm'].sort()
    );
  });

  it('hub-md / hub-lg / hub-mega use 4 / 6 / 8 rem font-size', () => {
    expect(STICKER_VARIANTS['hub-md'].fontSize).toBe('4rem');
    expect(STICKER_VARIANTS['hub-lg'].fontSize).toBe('6rem');
    expect(STICKER_VARIANTS['hub-mega'].fontSize).toBe('8rem');
  });

  it('sat-lg uses font-size 1.75rem and padding 20×32', () => {
    const v = STICKER_VARIANTS['sat-lg'];
    expect(v.fontSize).toBe('1.75rem');
    expect(v.padding).toBe('20px 32px');
  });

  it('renders sat-lg by default and applies variant styles', () => {
    const { container } = render(<Sticker>hello</Sticker>);
    const el = container.firstChild;
    expect(el.style.fontSize).toBe('1.75rem');
    expect(el.style.padding).toBe('20px 32px');
  });

  it('honors an explicit variant override', () => {
    const { container } = render(<Sticker variant="kicker">kicker</Sticker>);
    expect(container.firstChild.style.fontSize).toBe('1.25rem');
  });

  it('throws on unknown variant', () => {
    expect(() => render(<Sticker variant="bogus">x</Sticker>)).toThrow(/unknown variant/i);
  });

  it('still supports legacy bg/rotation props', () => {
    const { container } = render(
      <Sticker variant="sat-md" bg="secondary" rotation={-3}>x</Sticker>
    );
    const el = container.firstChild;
    expect(el.style.background).toBe('rgb(255, 217, 61)');   // #FFD93D
    expect(el.style.transform).toBe('rotate(-3deg)');
  });

  it('legacy border/padding/shadow overrides take effect', () => {
    const { container } = render(
      <Sticker variant="sat-lg" border={2} padding="8px 16px" shadow="sm">x</Sticker>
    );
    const el = container.firstChild;
    expect(el.style.border).toBe('2px solid rgb(0, 0, 0)');
    expect(el.style.padding).toBe('8px 16px');
    expect(el.style.boxShadow).toBe('4px 4px 0 0 #000');  // sm shadow
  });
});
