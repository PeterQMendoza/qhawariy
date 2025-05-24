from pulp import (
    LpProblem,
    LpMinimize,
    LpVariable,
    lpSum,
    LpStatus,
    value,
    LpInteger,
    LpContinuous
)


def solve_milp(T, demand, c, B, R, f, h):
    """
    Endpoint que resuelve el modelo MILP para la planificación de salidas en un sistema
    de transporte.
    Se espera un JSON de entrada con la siguiente estructura:
    {
      "T": 5,                     # Número total de intervalos del día.
      "demand": [100, 150, 90, 200, 80],   # Demanda de pasajeros por intervalo.
      "c": 50,                    # Capacidad del bus (número de pasajeros por viaje).
      "B": 10,                    # Número total de buses disponibles.
      "R": 2,                     # Número de intervalos que se requieren para un bus
            en completar el recorrido.
      "f": 5,                     # Costo operativo asociado a una salida.
      "h": 10                     # Costo unitario de insatisfacción por pasajero no
            atendido.
    }
    La respuesta incluirá el estado de la solución, el costo total y los valores
    óptimos de las variables:
      - y: número de salidas programadas por intervalo.
      - z: cantidad de demanda insatisfecha (si ocurre).
    """
    try:
        # data = request.get_json()

        # Extracción y validación de parámetros
        # T = data.get('T')
        # demand = data.get('demand')
        # c = data.get('c')
        # B = data.get('B')
        # R = data.get('R')
        # f = data.get('f')
        # h = data.get('h')

        if (
            T is None or
            demand is None or
            c is None or
            B is None or
            R is None or
            f is None or
            h is None
        ):
            # return jsonify({"error": "Faltan los parámetros necesarios."}), 400
            print("error: Faltan los parámetros necesarios.")

        if T != len(demand):
            # return jsonify({"error": "La longitud de la lista de demanda debe ser
            # igual a T."}), 400
            print("error: La longitud de la lista de demanda debe ser igual a T.")

        # Creación del modelo MILP
        prob = LpProblem("Planificacion_Transporte", LpMinimize)

        # Variables de decisión:
        # y[j]: número entero de salidas programadas en el intervalo j.
        # z[j]: demanda insatisfecha (exceso) en el intervalo j.
        y = LpVariable.dicts("y", list(range(T)), lowBound=0, cat=LpInteger)
        z = LpVariable.dicts("z", list(range(T)), lowBound=0, cat=LpContinuous)

        # Función objetivo: minimizar el costo total operacional más la penalización
        # por demanda no atendida.
        prob += lpSum([f * y[j] + h * z[j] for j in range(T)]), "CostoTotal"

        # Restricción 1: Satisfacción de la demanda o registro de déficit.
        for j in range(T):
            prob += c * y[j] + z[j] >= demand[j], f"RangoDemanda_{j}"

        # Restricción 2: Disponibilidad de flota en cada intervalo.
        for j in range(T):
            prob += y[j] <= B, f"Flota_{j}"

        # Restricción 3: Intervalo mínimo entre salidas de un bus (para un ciclo de
        # viaje que dura R intervalos)
        # Para cada intervalo j, la suma de salidas en el rango [max(0, j-R+1), j] debe
        # ser menor o igual a B
        for j in range(T):
            inicio = max(0, j - R + 1)
            prob += lpSum([y[k] for k in range(inicio, j + 1)]) <= B, f"Intervalo_{j}"

        # Resolución del modelo
        prob.solve()

        # Preparar la respuesta con los resultados.
        solution = {
            "status": LpStatus[prob.status],
            "TotalCost": value(prob.objective),
            "salidas_por_intervalo": {str(j): y[j].varValue for j in range(T)},
            "demanda_insatisfecha": {str(j): z[j].varValue for j in range(T)}
        }

        # return jsonify(solution)
        print(solution)

    except Exception as e:
        print({"error": str(e)})


if __name__ == '__main__':
    solve_milp(T=5, demand=[100, 150, 90, 200, 80], c=17, B=49, R=2, f=5, h=10)
