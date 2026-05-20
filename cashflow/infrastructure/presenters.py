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
                month_num = t.due_date.month
                if t.type == "inflow" or t.amount.value >= 0:
                    inflows_by_month[month_num].append(t)
                else:
                    outflows_by_month[month_num].append(t)
                    
        inflows_grouped = []
        for month_num, txs in sorted(inflows_by_month.items()):
            month_name = MONTH_NAMES.get(month_num, "OUTRO")
            txs_sorted = sorted(txs, key=lambda tx: tx.due_date)
            total = sum(tx.amount.value for tx in txs_sorted)
            tx_list = []
            for tx in txs_sorted:
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
        for month_num, txs in sorted(outflows_by_month.items()):
            month_name = MONTH_NAMES.get(month_num, "OUTRO")
            txs_sorted = sorted(txs, key=lambda tx: tx.due_date)
            total = sum(abs(tx.amount.value) for tx in txs_sorted)
            tx_list = []
            for tx in txs_sorted:
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
