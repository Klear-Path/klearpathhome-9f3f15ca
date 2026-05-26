import { Helmet } from "react-helmet-async";
import { Layout } from "@/components/layout/Layout";

const PrivacyPolicy = () => (
  <Layout>
    <Helmet>
      <title>Privacy Policy | Klear Path Home, Inc.</title>
      <meta name="description" content="How Klear Path Home, Inc. collects, uses, and protects information on klearpathhome.org, including Google Analytics and donation processing." />
      <link rel="canonical" href="https://klearpathhome.org/privacy-policy" />
    </Helmet>

    <section className="py-16 lg:py-20 bg-primary text-primary-foreground">
      <div className="container-wide section-padding max-w-3xl">
        <h1 className="text-4xl lg:text-5xl font-serif font-bold mb-4">Privacy Policy</h1>
        <p className="text-primary-foreground/80">Effective Date: May 26, 2026</p>
      </div>
    </section>

    <section className="py-16">
      <article className="container-wide section-padding max-w-3xl prose prose-lg text-foreground space-y-6">
        <p className="text-muted-foreground leading-relaxed">
          Klear Path Home, Inc. ("Klear Path," "we," "us," or "our") is a 501(c)(3) nonprofit
          organization (EIN 41-3156622) headquartered at 410 Hopkins Ct, North Wales, PA 19454.
          This Privacy Policy explains how we collect, use, and safeguard information when you
          visit <strong>klearpathhome.org</strong> or interact with our programs.
        </p>

        <h2 className="text-2xl font-serif font-semibold pt-4">1. Information We Collect</h2>
        <p className="text-muted-foreground leading-relaxed">
          We only collect personal information you voluntarily provide—such as your name, email
          address, phone number, or message—through our contact, volunteer, and partnership
          forms. When you make a donation, payment information is processed directly by Stripe;
          Klear Path never stores your credit card number on our servers.
        </p>

        <h2 className="text-2xl font-serif font-semibold pt-4">2. Cookies & Google Analytics</h2>
        <p className="text-muted-foreground leading-relaxed">
          We use <strong>Google Analytics 4</strong> with IP anonymization enabled to understand
          aggregate site usage and improve our content. Google Analytics sets cookies that may
          collect non-personally identifiable usage data (pages visited, device type, approximate
          region). You can opt out at any time using the{" "}
          <a href="https://tools.google.com/dlpage/gaoptout" className="underline" target="_blank" rel="noopener noreferrer">
            Google Analytics Opt-Out Browser Add-on
          </a>.
        </p>

        <h2 className="text-2xl font-serif font-semibold pt-4">3. How We Use Your Information</h2>
        <p className="text-muted-foreground leading-relaxed">
          We use submitted information solely to respond to inquiries, coordinate volunteer or
          partnership opportunities, deliver donation receipts, and share mission-related updates
          when you request them. We <strong>do not sell, rent, or trade</strong> donor or visitor
          information to any third party.
        </p>

        <h2 className="text-2xl font-serif font-semibold pt-4">4. Donor Data Protection</h2>
        <p className="text-muted-foreground leading-relaxed">
          Donor records are stored on secure, access-controlled infrastructure and shared only
          with staff, board members, and contractors who require them for fulfillment, accounting,
          or legal compliance. Stripe is our PCI-DSS Level 1 certified payment processor.
        </p>

        <h2 className="text-2xl font-serif font-semibold pt-4">5. Data Security & HTTPS</h2>
        <p className="text-muted-foreground leading-relaxed">
          All traffic to klearpathhome.org is served over HTTPS/TLS encryption. We apply
          industry-standard administrative and technical safeguards to protect personal data.
        </p>

        <h2 className="text-2xl font-serif font-semibold pt-4">6. Your Rights</h2>
        <p className="text-muted-foreground leading-relaxed">
          You may request to review, correct, or delete any personal information we hold by
          emailing <a href="mailto:info@klearpathhome.org" className="underline">info@klearpathhome.org</a>.
        </p>

        <h2 className="text-2xl font-serif font-semibold pt-4">7. Children's Privacy</h2>
        <p className="text-muted-foreground leading-relaxed">
          Our site is not directed to children under 13, and we do not knowingly collect personal
          information from children.
        </p>

        <h2 className="text-2xl font-serif font-semibold pt-4">8. Policy Updates</h2>
        <p className="text-muted-foreground leading-relaxed">
          We may update this Privacy Policy from time to time. Material changes will be posted on
          this page with a revised effective date.
        </p>

        <h2 className="text-2xl font-serif font-semibold pt-4">9. Contact</h2>
        <p className="text-muted-foreground leading-relaxed">
          Klear Path Home, Inc.<br />
          410 Hopkins Ct, North Wales, PA 19454<br />
          <a href="mailto:info@klearpathhome.org" className="underline">info@klearpathhome.org</a>
        </p>
      </article>
    </section>
  </Layout>
);

export default PrivacyPolicy;