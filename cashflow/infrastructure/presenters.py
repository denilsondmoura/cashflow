from collections import defaultdict
from typing import List
from cashflow.application.ports.outbound.presenters import TransactionGroupPresenter
from cashflow.domain.entities import Transaction

class DjangoTransactionGroupPresenter(TransactionGroupPresenter):
    def group_transactions(self, transactions: List[Transaction]) -> dict:
        MONTH_NAMES = {
            1: "JANEIRO", 2: "FEVEREIRO", 3: "MARÇO", 4: "ABRIL", 5: "MAIO", 6: "JUNHO",
            7: "JULHO", 8: "AGOSTO", 9: "SETEMBRO", 10: "OUTUBRO", 11: "NOVEMBRO", 12: "DEZEMBRO"
        }
        
        inflows_by_month = defaultdict(list)
        outflows_by_month = defaultdict(list)
        
        if transactions:
            for t in transactions:
                month_name = MONTH_NAMES.get(t.due_date.month, "OUTRO")
                if t.type == "inflow" or t.amount.value >= 0:
                    inflows_by_month[month_name].append(t)
                else:
                    outflows_by_month[month_name].append(t)
                    
        if not inflows_by_month and not outflows_by_month:
            mock_inflows_junho = [
                {"due_date_str": "01/06", "description": "salário empresa A", "amount_formatted": "R$ 5.300,00"},
                {"due_date_str": "02/06", "description": "salário empresa B", "amount_formatted": "R$ 1.800,00"},
                {"due_date_str": "03/06", "description": "Restituição IR", "amount_formatted": "R$ 1.800,00"},
                {"due_date_str": "04/06", "description": "ticket", "amount_formatted": "R$ 600,00"},
            ]
            inflows_grouped = [
                {"month": "JUNHO", "transactions": mock_inflows_junho, "total_formatted": "R$ 9.500,00"},
                {"month": "JULHO", "transactions": [], "total_formatted": "R$ 9.100,00"},
                {"month": "AGOSTO", "transactions": [], "total_formatted": "R$ 9.100,00"},
            ]
            
            mock_outflows_junho = [
                {"due_date_str": "01/06", "description": "fatura do cartão", "amount_formatted": "R$ 1.300,00"},
                {"due_date_str": "02/06", "description": "conta de energia", "amount_formatted": "R$ 200,00"},
                {"due_date_str": "03/06", "description": "Seguro da moto", "amount_formatted": "R$ 116,00"},
                {"due_date_str": "04/06", "description": "Monitor philips evnia", "amount_formatted": "R$ 800,00"},
            ]
            outflows_grouped = [
                {"month": "JUNHO", "transactions": mock_outflows_junho, "total_formatted": "R$ 2.416,00"},
                {"month": "JULHO", "transactions": [], "total_formatted": "R$ 9.100,00"},
                {"month": "AGOSTO", "transactions": [], "total_formatted": "R$ 9.100,00"},
            ]
        else:
            inflows_grouped = []
            for month_name, txs in inflows_by_month.items():
                total = sum(tx.amount.value for tx in txs)
                tx_list = []
                for tx in txs:
                    tx_list.append({
                        "id": tx.id,
                        "due_date_str": tx.due_date.strftime("%d/%m"),
                        "due_date_iso": tx.due_date.strftime("%Y-%m-%d"),
                        "description": tx.description,
                        "amount_formatted": f"R$ {tx.amount.value:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                        "amount_raw": f"{tx.amount.value:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                        "cleared": tx.cleared,
                        "type": tx.type
                    })
                inflows_grouped.append({
                    "month": month_name,
                    "transactions": tx_list,
                    "total_formatted": f"R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                })
                
            outflows_grouped = []
            for month_name, txs in outflows_by_month.items():
                total = sum(abs(tx.amount.value) for tx in txs)
                tx_list = []
                for tx in txs:
                    tx_list.append({
                        "id": tx.id,
                        "due_date_str": tx.due_date.strftime("%d/%m"),
                        "due_date_iso": tx.due_date.strftime("%Y-%m-%d"),
                        "description": tx.description,
                        "amount_formatted": f"R$ {abs(tx.amount.value):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                        "amount_raw": f"{abs(tx.amount.value):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                        "cleared": tx.cleared,
                        "type": tx.type
                    })
                outflows_grouped.append({
                    "month": month_name,
                    "transactions": tx_list,
                    "total_formatted": f"R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                })
                
        return {
            "inflows_grouped": inflows_grouped,
            "outflows_grouped": outflows_grouped
        }
