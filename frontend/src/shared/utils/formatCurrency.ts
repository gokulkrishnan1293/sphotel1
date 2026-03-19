// INVARIANT: all money is integer paise. NEVER pass float rupees.
// ₹150.00 = 15000 paise. NEVER use floating point arithmetic on money values.
// NEVER divide by 100 anywhere except this function.
export const formatCurrency = (paise: number): string => {
  return `₹${(paise / 100).toFixed(2)}`
}
