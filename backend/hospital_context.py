from database import (
    get_admin_doctors,
    get_admin_rooms,
    get_dashboard_data
)

def build_hospital_context():

    doctors = get_admin_doctors()
    rooms = get_admin_rooms()
    dashboard = get_dashboard_data()

    context = "\nDoctors:\n"

    for d in doctors:
        context += (
            f"{d[1]} | {d[2]} | "
            f"{d[4]} | Fee ₹{d[5]}\n"
        )

    context += "\nRooms:\n"

    for r in rooms:
        context += (
            f"{r[1]} | {r[2]} | "
            f"₹{r[3]} | {r[4]}\n"
        )

    context += f"\nDashboard:\n{dashboard}"

    return context