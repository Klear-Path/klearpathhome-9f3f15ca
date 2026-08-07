import { useState } from "react";
import { Mail } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { HoneypotField } from "@/components/HoneypotField";
import { submitContactSubmission, submissionErrorMessage } from "@/lib/forms";

export function EmailCapture() {
  const [email, setEmail] = useState("");
  const [firstName, setFirstName] = useState("");
  const [honeypot, setHoneypot] = useState("");
  const [status, setStatus] = useState<"idle" | "sending" | "sent" | "error">("idle");
  const [errorMessage, setErrorMessage] = useState("");

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!email || status === "sending") return;

    setStatus("sending");
    setErrorMessage("");

    try {
      await submitContactSubmission({
        form: "newsletter",
        name: firstName,
        email,
        honeypot,
      });
      setStatus("sent");
    } catch (error) {
      setErrorMessage(submissionErrorMessage(error));
      setStatus("error");
    }
  };

  return (
    <section className="py-16 bg-secondary border-y border-border" data-section="email-capture">
      <div className="container-wide section-padding">
        <div className="grid lg:grid-cols-[1fr_1.1fr] gap-8 items-center">
          <div>
            <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center mb-4">
              <Mail className="w-6 h-6 text-primary" />
            </div>
            <h2 className="text-3xl font-serif font-bold text-foreground mb-4">
              Stay Connected To The Mission
            </h2>
            <p className="text-muted-foreground leading-relaxed max-w-xl">
              Receive updates, impact stories, volunteer opportunities, and ways to support long-term housing stability initiatives.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="relative bg-card border border-border rounded-2xl p-6 shadow-soft">
            <HoneypotField id="newsletter-website" value={honeypot} onChange={setHoneypot} />
            <div className="grid sm:grid-cols-2 gap-3 mb-4">
              <Input
                placeholder="First name"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
              />
              <Input
                type="email"
                required
                placeholder="Email address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>

            <Button type="submit" data-cta="email-capture-submit" disabled={status === "sending"}>
              {status === "sending" ? "Adding you…" : "Stay Connected"}
            </Button>

            {status === "sent" && (
              <p className="text-sm text-primary font-medium mt-4">
                You’re on the list. More updates coming soon.
              </p>
            )}

            {status === "error" && (
              <p role="alert" className="text-sm text-destructive font-medium mt-4">
                {errorMessage}
              </p>
            )}

            <p className="text-xs text-muted-foreground mt-4">
              No spam. Just mission updates, impact milestones, and opportunities to help.
            </p>
          </form>
        </div>
      </div>
    </section>
  );
}
