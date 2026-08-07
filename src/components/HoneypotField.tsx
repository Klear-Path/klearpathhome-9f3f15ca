/**
 * A decoy input that people never see and bots usually fill. Pass the value to
 * the submit helpers in @/lib/forms — a non-empty value drops the submission.
 *
 * Hidden with an off-screen wrapper rather than `display: none`, because some
 * bots skip fields that are display-none. `aria-hidden` and `tabIndex={-1}`
 * keep it out of the way of screen readers and keyboard navigation.
 */
interface HoneypotFieldProps {
  value: string;
  onChange: (value: string) => void;
  /** Must be unique when more than one form renders on a page. */
  id?: string;
}

export function HoneypotField({ value, onChange, id = "website" }: HoneypotFieldProps) {
  return (
    <div
      aria-hidden="true"
      className="absolute left-[-9999px] top-auto h-px w-px overflow-hidden"
    >
      <label htmlFor={id}>Leave this field empty</label>
      <input
        id={id}
        name={id}
        type="text"
        tabIndex={-1}
        autoComplete="off"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
    </div>
  );
}
