/**
 * Every public form on the site submits through this module.
 *
 * Rows go to Supabase (`help_requests` and `contact_submissions`), which are
 * insert-only for the publishable key — see
 * supabase/migrations/20260807000000_form_submissions.sql. Nothing here reads
 * data back, so a leaked anon key cannot expose submissions.
 */

import { supabase } from "@/integrations/supabase/client";

/** Trim a value and collapse blanks to null, which is what the columns expect. */
function clean(value: string | undefined | null): string | null {
  const trimmed = value?.trim();
  return trimmed ? trimmed : null;
}

/**
 * Bots fill in every field they find, including ones hidden from people. A
 * filled honeypot means we drop the submission and report success, so the bot
 * has no signal to retry with.
 */
function isBot(honeypot: string | undefined): boolean {
  return Boolean(honeypot && honeypot.trim());
}

export class FormSubmissionError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "FormSubmissionError";
  }
}

const GENERIC_FAILURE =
  "We couldn't save your request. Please call us instead — we don't want you waiting on a form that isn't working.";

/* -------------------------------------------------------------------------- */
/* Help requests                                                              */
/* -------------------------------------------------------------------------- */

export type HelpRequestInput = {
  name: string;
  phone?: string;
  email?: string;
  county?: string;
  /** Document ids from the /get-help checklist. */
  documents: string[];
  documentsOther?: string;
  deadline?: string;
  veteran?: boolean;
  notes?: string;
  honeypot?: string;
};

export async function submitHelpRequest(input: HelpRequestInput): Promise<void> {
  if (isBot(input.honeypot)) return;

  const name = clean(input.name);
  const phone = clean(input.phone);
  const email = clean(input.email);

  if (!name) {
    throw new FormSubmissionError("Please tell us your name.");
  }
  if (!phone && !email) {
    throw new FormSubmissionError(
      "Please give us a phone number or an email address so we can reach you.",
    );
  }
  if (input.documents.length === 0) {
    throw new FormSubmissionError("Please choose at least one document.");
  }

  const { error } = await supabase.from("help_requests").insert({
    name,
    phone,
    email,
    county: clean(input.county),
    documents: input.documents,
    documents_other: clean(input.documentsOther),
    deadline: clean(input.deadline),
    veteran: Boolean(input.veteran),
    notes: clean(input.notes),
    source: "get-help",
  });

  if (error) {
    console.error("help_requests insert failed", error);
    throw new FormSubmissionError(GENERIC_FAILURE);
  }
}

/* -------------------------------------------------------------------------- */
/* Contact, volunteer, get-involved, newsletter                               */
/* -------------------------------------------------------------------------- */

export type ContactFormKind =
  | "contact"
  | "volunteer"
  | "get-involved"
  | "newsletter";

export type ContactSubmissionInput = {
  form: ContactFormKind;
  name?: string;
  email?: string;
  phone?: string;
  organization?: string;
  inquiryType?: string;
  subject?: string;
  message?: string;
  interests?: string[];
  availability?: string;
  honeypot?: string;
};

export async function submitContactSubmission(
  input: ContactSubmissionInput,
): Promise<void> {
  if (isBot(input.honeypot)) return;

  const email = clean(input.email);
  const phone = clean(input.phone);

  if (!email && !phone) {
    throw new FormSubmissionError(
      "Please give us an email address or a phone number so we can reply.",
    );
  }

  const { error } = await supabase.from("contact_submissions").insert({
    form: input.form,
    name: clean(input.name),
    email,
    phone,
    organization: clean(input.organization),
    inquiry_type: clean(input.inquiryType),
    subject: clean(input.subject),
    message: clean(input.message),
    interests: input.interests ?? [],
    availability: clean(input.availability),
  });

  if (error) {
    console.error("contact_submissions insert failed", error);
    throw new FormSubmissionError(GENERIC_FAILURE);
  }
}

/** Message to show a user when a submission fails for an unknown reason. */
export function submissionErrorMessage(error: unknown): string {
  return error instanceof FormSubmissionError ? error.message : GENERIC_FAILURE;
}
