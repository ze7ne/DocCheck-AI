
from fpdf import FPDF, XPos, YPos
from datetime import date


class LoanPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, "PINNACLE FINANCE GROUP LLC  |  PERSONAL LOAN AGREEMENT", align="C",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2)
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 5, f"Page {self.page_no()} | Confidential - For borrower use only", align="C")

    def section_title(self, title):
        self.ln(4)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(30, 30, 30)
        self.set_fill_color(240, 243, 250)
        self.cell(0, 8, f"  {title}", fill=True,
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2)

    def body_text(self, text, indent=0):
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(50, 50, 50)
        self.set_x(10 + indent)
        self.multi_cell(190 - indent, 5.5, text)
        self.ln(1)

    def kv(self, label, value, bold_value=False):
        self.set_font("Helvetica", "B", 9.5)
        self.set_text_color(80, 80, 80)
        self.cell(62, 6, label + ":", new_x=XPos.RIGHT, new_y=YPos.TOP)
        style = "B" if bold_value else ""
        self.set_font("Helvetica", style, 9.5)
        self.set_text_color(20, 20, 20)
        self.cell(0, 6, value, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def clause(self, number, title, text):
        self.set_font("Helvetica", "B", 9.5)
        self.set_text_color(30, 30, 30)
        self.cell(0, 6, f"{number}. {title}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.body_text(text, indent=5)


pdf = LoanPDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()

# Title block
pdf.set_font("Helvetica", "B", 16)
pdf.set_text_color(15, 30, 80)
pdf.cell(0, 10, "PERSONAL LOAN AGREEMENT", align="C",
         new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.set_font("Helvetica", "", 10)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 6,
         f"Contract No. PFG-2026-04-88421   |   Date: {date.today().strftime('%B %d, %Y')}",
         align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.ln(6)

# 1. Parties
pdf.section_title("1. PARTIES TO THE AGREEMENT")
pdf.kv("Lender", "Pinnacle Finance Group LLC, 1250 Capital Ave, Suite 400, New York, NY 10001")
pdf.kv("Borrower", "John M. Hartwell")
pdf.kv("Borrower Address", "742 Evergreen Terrace, Springfield, IL 62704")
pdf.kv("Borrower SSN (last 4)", "****-**-7834")
pdf.ln(2)

# 2. Loan Terms
pdf.section_title("2. LOAN TERMS")
pdf.kv("Principal Amount", "$18,500.00", bold_value=True)
pdf.kv("Annual Percentage Rate (APR)", "24.99%", bold_value=True)
pdf.kv("Loan Term", "48 months (4 years)")
pdf.kv("Monthly Payment", "$576.43")
pdf.kv("Total Repayment Amount", "$27,668.64")
pdf.kv("Total Interest Paid", "$9,168.64")
pdf.kv("First Payment Due", "May 15, 2026")
pdf.kv("Disbursement Method", "Direct deposit within 3 business days (net of fees)")
pdf.ln(2)

# 3. Fees
pdf.section_title("3. ORIGINATION & PROCESSING FEES")
pdf.body_text(
    "3.1  ORIGINATION FEE: Borrower agrees to pay a non-refundable loan origination fee equal to "
    "6% of the principal amount ($1,110.00). This fee is deducted from the disbursed funds at "
    "closing. The borrower will receive $17,390.00 net, not $18,500.00."
)
pdf.body_text(
    "3.2  ADMINISTRATIVE PROCESSING FEE: A one-time administrative fee of $299.00 will be charged "
    "to the borrower's account on the date of the first statement. This fee covers document "
    "preparation, credit report retrieval, identity verification, and account setup costs."
)
pdf.body_text(
    "3.3  MONTHLY ACCOUNT MAINTENANCE FEE: Borrower shall pay a monthly account maintenance fee "
    "of $12.95 per billing cycle, assessed automatically to the loan balance on each statement "
    "date. This fee is separate from the scheduled monthly payment and does not reduce principal."
)
pdf.body_text(
    "3.4  PAPER STATEMENT FEE: If the borrower does not enroll in paperless electronic statements "
    "within 30 days of loan origination, a paper statement fee of $5.95 per month will be applied."
)
pdf.body_text(
    "3.5  PAYMENT PROCESSING FEE: Payments made via telephone agent or in-branch will incur a "
    "payment processing fee of $9.95 per transaction. Online and automatic ACH payments are free."
)

# 4. Penalties
pdf.section_title("4. LATE PAYMENTS, DEFAULT & PENALTIES")
pdf.body_text(
    "4.1  GRACE PERIOD: Borrower has a grace period of 5 calendar days after the due date before "
    "a late fee is assessed. There is NO grace period for the first payment."
)
pdf.body_text(
    "4.2  LATE PAYMENT FEE: If payment is not received within the grace period, Lender will "
    "charge a late fee of the GREATER of $39.00 or 5% of the overdue payment amount. "
    "This fee is charged per occurrence."
)
pdf.body_text(
    "4.3  RETURNED PAYMENT FEE (NSF): If a payment is returned due to insufficient funds or a "
    "stopped check, a returned payment fee of $45.00 will be assessed. The Lender reserves the "
    "right to re-present the payment up to two additional times, each attempt potentially "
    "incurring a further NSF fee."
)
pdf.body_text(
    "4.4  DEFAULT: Borrower will be considered in default if: (a) any payment is more than 30 "
    "days past due; (b) Borrower files for bankruptcy; (c) any information on the loan "
    "application is found to be materially false; or (d) Borrower's employment status changes "
    "materially without notice to Lender."
)
pdf.body_text(
    "4.5  ACCELERATION CLAUSE: Upon default, the Lender may, at its sole discretion, declare "
    "the entire remaining unpaid balance of the loan, together with accrued interest and all "
    "fees, immediately due and payable in full without further notice to Borrower."
)
pdf.body_text(
    "4.6  DEFAULT INTEREST RATE: Upon default, the interest rate applicable to the outstanding "
    "balance shall automatically increase to 34.99% APR until the account is brought current "
    "or paid in full."
)
pdf.body_text(
    "4.7  COLLECTION COSTS: Borrower agrees to pay all costs of collection including, without "
    "limitation, reasonable attorney fees (up to 25% of the outstanding balance), court costs, "
    "and third-party collection agency fees, should Lender refer the account for collection."
)

# 5. Prepayment
pdf.section_title("5. PREPAYMENT")
pdf.body_text(
    "5.1  PREPAYMENT PENALTY: If Borrower repays the loan in full before the end of Month 24 "
    "(the first 24 months of the loan term), a prepayment penalty equal to 3% of the original "
    "principal amount ($555.00) will be charged. No prepayment penalty applies after Month 24."
)
pdf.body_text(
    "5.2  PARTIAL PREPAYMENTS: Partial prepayments do not reduce the scheduled monthly payment "
    "amount. Any extra amounts paid will be applied to the final payments first, not to reduce "
    "the principal outstanding, unless Borrower submits a written request specifying principal "
    "reduction."
)

# 6. Arbitration
pdf.section_title("6. MANDATORY BINDING ARBITRATION & CLASS ACTION WAIVER")
pdf.body_text(
    "6.1  ARBITRATION AGREEMENT: ANY DISPUTE, CLAIM OR CONTROVERSY ARISING OUT OF OR RELATING "
    "TO THIS AGREEMENT SHALL BE RESOLVED EXCLUSIVELY BY FINAL AND BINDING ARBITRATION, AND NOT "
    "IN COURT. Borrower waives any right to a jury trial or to participate in a class action "
    "lawsuit. Arbitration will be conducted by JAMS under its Consumer Arbitration Rules. "
    "Lender will pay the arbitration filing fee up to $250. Borrower is responsible for any "
    "fees above that amount."
)
pdf.body_text(
    "6.2  CLASS ACTION WAIVER: Borrower and Lender agree that claims may only be brought in an "
    "individual capacity and not as a plaintiff or class member in any purported class or "
    "representative proceeding. This waiver is a material inducement for Lender to extend credit."
)

# 7. Variable Rate
pdf.section_title("7. VARIABLE RATE PROVISIONS")
pdf.body_text(
    "7.1  Although the initial APR is fixed at 24.99%, Lender reserves the right to modify the "
    "interest rate upon 30-day written notice to Borrower if: (a) Borrower's credit score drops "
    "below 620; (b) Borrower misses two or more payments in any 12-month period; or (c) "
    "applicable law or regulatory changes require an adjustment. Maximum rate: 34.99% APR."
)

# 8. Data Sharing
pdf.section_title("8. CONSENT TO MARKETING & DATA SHARING")
pdf.body_text(
    "8.1  By signing this Agreement, Borrower consents to receive marketing communications from "
    "Pinnacle Finance Group and its affiliated partners via phone, email, and postal mail. "
    "Borrower further consents to sharing of financial information with affiliated third parties "
    "for cross-selling purposes. To opt out, Borrower must submit a written opt-out request "
    "within 30 days of signing."
)
pdf.body_text(
    "8.2  Lender may share Borrower's payment history, account status, and contact information "
    "with credit bureaus, affiliates, and data analytics partners."
)

# 9. Insurance
pdf.section_title("9. OPTIONAL CREDIT INSURANCE (AUTO-ENROLLED)")
pdf.body_text(
    "9.1  Borrower has been offered optional Loan Protection Insurance at a premium of $42.50 "
    "per month, which covers monthly loan payments in the event of involuntary unemployment, "
    "disability, or death. By not checking the opt-out box below and signing this agreement, "
    "Borrower AGREES to enroll in this optional insurance and authorizes the monthly premium "
    "to be added to the loan balance."
)
pdf.body_text("   [  ]  I DO NOT wish to enroll in Loan Protection Insurance.")

# 10. Governing Law
pdf.section_title("10. GOVERNING LAW & MISCELLANEOUS")
pdf.body_text(
    "10.1  This Agreement shall be governed by the laws of the State of Delaware, without "
    "regard to its conflict of law principles, regardless of Borrower's state of residence."
)
pdf.body_text(
    "10.2  Lender reserves the right to assign or transfer this Agreement to a third-party "
    "servicer without Borrower's consent. Borrower's obligations remain unchanged."
)
pdf.body_text(
    "10.3  This Agreement constitutes the entire agreement between the parties and supersedes "
    "all prior communications, representations, or agreements, whether written or oral."
)

# Signature block
pdf.ln(6)
pdf.set_draw_color(200, 200, 200)
pdf.set_line_width(0.3)
pdf.line(10, pdf.get_y(), 200, pdf.get_y())
pdf.ln(6)

pdf.set_font("Helvetica", "B", 10)
pdf.set_text_color(30, 30, 30)
pdf.cell(0, 6, "ACKNOWLEDGMENT & SIGNATURE", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.ln(2)
pdf.set_font("Helvetica", "", 9)
pdf.set_text_color(60, 60, 60)
pdf.multi_cell(0, 5.5,
    "By signing below, Borrower acknowledges that they have read and understood this entire "
    "Agreement, including all fee schedules, penalty provisions, the mandatory arbitration "
    "clause, and the class action waiver. Borrower confirms they had sufficient opportunity "
    "to review the Agreement and consult independent legal counsel before signing."
)
pdf.ln(8)

pdf.set_font("Helvetica", "", 9.5)
pdf.cell(90, 6, "Borrower Signature: _________________________",
         new_x=XPos.RIGHT, new_y=YPos.TOP)
pdf.cell(0, 6, "Date: ___________________", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.ln(4)
pdf.cell(90, 6, "Printed Name: _________________________",
         new_x=XPos.RIGHT, new_y=YPos.TOP)
pdf.cell(0, 6, "Lender Representative: ___________________", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.ln(8)

pdf.set_font("Helvetica", "I", 8)
pdf.set_text_color(140, 140, 140)
pdf.multi_cell(0, 4.5,
    "NOTICE: This is a legally binding contract. You have the right to cancel this agreement "
    "within 3 business days of signing (Right of Rescission) by providing written notice to "
    "Pinnacle Finance Group LLC at the address above. After 3 business days, cancellation "
    "fees apply per Section 5.1."
)

output_path = "/Users/ernurteginbaev/Desktop/CODE/AI_Parser_fot_FinanceDoc/AI_DocCheck/sample_loan_agreement.pdf"
pdf.output(output_path)
print(f"Sample PDF created: {output_path}")
