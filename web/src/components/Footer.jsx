export default function Footer({ meta }) {
  return (
    <footer className="footer">
      <p className="footer__note">
        Insults here target conduct and character, in the tradition of Shakespearean insult
        generators. Slurs aimed at people for who they are, and sexual content, are deliberately
        excluded from the vocabulary. The vulgar register is profanity, nothing more.
      </p>
      <p className="footer__meta">
        insult-generator-5000 · v{meta.version} · No tracking, no third-party requests.
      </p>
    </footer>
  );
}
