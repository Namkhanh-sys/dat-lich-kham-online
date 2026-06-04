import hashlib


class Pricing:
    MIN_FEE = 100_000
    STEP = 10_000
    STEPS = 6

    @classmethod
    def consultation_fee(cls, doctor_id):
        """Return a stable consultation fee from 100,000 to 150,000 VND."""
        digest = hashlib.sha256(str(doctor_id).encode('utf-8')).hexdigest()
        bucket = int(digest[:8], 16) % cls.STEPS
        return cls.MIN_FEE + bucket * cls.STEP

    @staticmethod
    def format_vnd(amount):
        return f"{int(amount):,}".replace(",", ".") + "đ"
