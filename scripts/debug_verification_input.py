from verification_table import VerificationInput

print("class Mx:", getattr(VerificationInput, "Mx", None))
print("type class Mx:", type(getattr(VerificationInput, "Mx", None)))
vi = VerificationInput()
print("instance Mx:", vi.Mx)
print("type instance Mx:", type(vi.Mx))
print("hasattr Mx", hasattr(vi, "Mx"))
print("hasattr M", hasattr(vi, "M"))
print(
    "class dict keys sample",
    [k for k in VerificationInput.__dict__.keys() if "Mx" in k or k in ("M", "T")],
)
