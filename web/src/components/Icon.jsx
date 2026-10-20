const PATHS = {
  flame: (
    <path
      fill="currentColor"
      stroke="none"
      d="M12 2.2c.5 3.3-1.9 4.8-3.5 7C7.1 11.1 6.4 12.5 6.4 14.2a5.6 5.6 0 0 0 11.2 0c0-2.2-1.1-3.8-2.2-5 .1 1.7-.4 2.7-1.5 3.3.6-3.9-.6-7.4-1.9-10.3z"
    />
  ),
  dice: (
    <>
      <rect x="3.5" y="3.5" width="17" height="17" rx="4.5" />
      <circle cx="8.6" cy="8.6" r="1.1" fill="currentColor" stroke="none" />
      <circle cx="15.4" cy="8.6" r="1.1" fill="currentColor" stroke="none" />
      <circle cx="12" cy="12" r="1.1" fill="currentColor" stroke="none" />
      <circle cx="8.6" cy="15.4" r="1.1" fill="currentColor" stroke="none" />
      <circle cx="15.4" cy="15.4" r="1.1" fill="currentColor" stroke="none" />
    </>
  ),
  copy: (
    <>
      <rect x="9" y="9" width="12" height="12" rx="2.5" />
      <path d="M5 15H4.5A2.5 2.5 0 0 1 2 12.5v-8A2.5 2.5 0 0 1 4.5 2h8A2.5 2.5 0 0 1 15 4.5V5" />
    </>
  ),
  check: <polyline points="20 6.5 9.5 17 4 11.5" />,
  star: (
    <polygon points="12 2.6 14.9 8.6 21.4 9.5 16.7 14.1 17.8 20.6 12 17.5 6.2 20.6 7.3 14.1 2.6 9.5 9.1 8.6 12 2.6" />
  ),
  link: (
    <>
      <path d="M10 13.5a4.5 4.5 0 0 0 6.4 0l3-3a4.5 4.5 0 0 0-6.4-6.4l-1.1 1.1" />
      <path d="M14 10.5a4.5 4.5 0 0 0-6.4 0l-3 3a4.5 4.5 0 0 0 6.4 6.4l1.1-1.1" />
    </>
  ),
  sun: (
    <>
      <circle cx="12" cy="12" r="4.2" />
      <path d="M12 2.5v2M12 19.5v2M4.6 4.6 6 6M18 18l1.4 1.4M2.5 12h2M19.5 12h2M4.6 19.4 6 18M18 6l1.4-1.4" />
    </>
  ),
  moon: <path d="M20.5 13.2A8.5 8.5 0 1 1 10.8 3.5a6.7 6.7 0 0 0 9.7 9.7z" />,
  search: (
    <>
      <circle cx="11" cy="11" r="6.5" />
      <path d="m20 20-4.2-4.2" />
    </>
  ),
  close: <path d="M6 6l12 12M18 6 6 18" />,
  arrow: <path d="M5 12h14M13 6l6 6-6 6" />,
  down: <path d="M6 9l6 6 6-6" />,
};

export default function Icon({ name, size = 20, className = "", title }) {
  return (
    <svg
      className={`icon ${className}`.trim()}
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      role={title ? "img" : undefined}
      aria-hidden={title ? undefined : true}
    >
      {title ? <title>{title}</title> : null}
      {PATHS[name]}
    </svg>
  );
}
