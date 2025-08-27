# Cálculos Automáticos para Sanes y Rifas

## Resumen de Implementación

Se han implementado funciones de cálculo automático para sanes y rifas que muestran información relevante y alertas de viabilidad en tiempo real en los formularios de creación.

## Funcionalidades Implementadas

### Para Sanes

#### Datos de Entrada:
- **Monto total**: Precio total del san
- **Número de participantes**: Total de personas que participarán
- **Frecuencia de pago**: Diaria, semanal, quincenal, mensual
- **Fecha de inicio**: Cuándo comienza el san
- **Fecha de fin**: Cuándo termina el san
- **Número de cuotas**: Cuántas cuotas se pagarán

#### Sugerencias Automáticas:
- **Fechas sugeridas**: Calcula automáticamente las fechas de inicio y fin óptimas
- **Duración del san**: Muestra la duración total en días
- **Periodos por mes**: Indica cuántos periodos de pago hay por mes

#### Cálculos Automáticos:
1. **Cuota por participante por periodo**: `precio_total / numero_cuotas` (cada participante paga el monto total dividido en cuotas)
2. **Número mínimo de periodos necesarios**: Basado en el número de cuotas
3. **Periodos disponibles**: Calculado según las fechas y frecuencia de pago
4. **Monto total aportado**: `cuota_por_participante * total_participantes` (cada participante paga la cuota completa)
5. **Diferencia**: `monto_total_aportado - precio_total`

#### Alertas de Viabilidad:
- ✅ **San viable**: Cuando todos los parámetros son correctos
- ⚠️ **Fechas insuficientes**: Si el número de cuotas excede los periodos disponibles
- ⚠️ **Monto insuficiente**: Si los parámetros no cubren el precio total
- ⚠️ **Fechas inválidas**: Si la fecha de fin es anterior a la de inicio
- ⚠️ **Participantes insuficientes**: Si hay menos de 2 participantes

### Para Rifas

#### Datos de Entrada:
- **Precio del ticket**: Costo por ticket
- **Cantidad total de tickets**: Número de tickets disponibles
- **Valor del premio** (opcional): Valor monetario del premio

#### Sugerencias Automáticas:
- **Precio de ticket sugerido**: Basado en el valor del premio
- **Total de tickets sugerido**: Para cubrir el premio con ganancia del 20%
- **Ganancia esperada**: Con los parámetros sugeridos
- **Porcentaje de ganancia**: Calculado automáticamente

#### Cálculos Automáticos:
1. **Recaudación mínima esperada**: `precio_ticket * total_tickets`
2. **Mínimo de participantes para cubrir premio**: `valor_premio / precio_ticket`
3. **Ganancia esperada**: `recaudacion_minima - valor_premio`
4. **Porcentaje de ganancia**: `(ganancia_esperada / recaudacion_minima) * 100`

#### Alertas de Viabilidad:
- ✅ **Rifa viable**: Cuando se cubre el premio y hay ganancia
- ⚠️ **Premio no cubierto**: Si la recaudación no alcanza para el premio
- ⚠️ **Pérdidas**: Si la rifa generaría pérdidas
- ⚠️ **Parámetros inválidos**: Si el precio del ticket o número de tickets es 0 o negativo

## Archivos Modificados

### 1. `sanes/utils.py`
- **Funciones agregadas**:
  - `calcular_san_contexto()`: Calcula métricas para sanes
  - `calcular_rifa_contexto()`: Calcula métricas para rifas
  - `calcular_fechas_sugeridas_san()`: Sugiere fechas óptimas para sanes
  - `calcular_parametros_sugeridos_rifa()`: Sugiere parámetros óptimos para rifas
  - `formatear_moneda()`: Formatea valores como moneda
  - `formatear_porcentaje()`: Formatea valores como porcentaje

### 2. `sanes/views.py`
- **Vistas modificadas**:
  - `SanCreateView`: Agregado manejo de cálculos en tiempo real
  - `RifaCreateView`: Agregado manejo de cálculos en tiempo real
- **Funcionalidades agregadas**:
  - Cálculos automáticos en `get_context_data()`
  - Manejo de peticiones AJAX en `post()`
  - Mejor manejo de errores en `form_valid()`

### 3. `sanes/templates/san/create_san.html`
- **Sección agregada**: "Cálculos Automáticos" que muestra:
  - Estado de viabilidad (verde/rojo)
  - Métricas calculadas en tarjetas
  - Alertas y mensajes informativos
- **JavaScript agregado**: Actualización en tiempo real con debouncing

### 4. `sanes/templates/raffle/rifa_create.html`
- **Sección agregada**: "Cálculos Automáticos" que muestra:
  - Estado de viabilidad (verde/rojo)
  - Métricas calculadas en tarjetas
  - Alertas y mensajes informativos
- **JavaScript agregado**: Actualización en tiempo real con debouncing

## Características Técnicas

### Cálculos en Tiempo Real
- Los cálculos se actualizan automáticamente cuando el usuario llena los campos requeridos
- Se ejecutan inmediatamente al cargar la página si hay datos en los campos
- Se usa debouncing (300ms) para ser más responsivo y evitar demasiadas peticiones al servidor
- Las peticiones AJAX solo actualizan la sección de cálculos, no toda la página
- Indicadores visuales de actualización (✓ Actualizado / ✗ Error)
- Validación de campos antes de enviar peticiones para optimizar recursos
- Validación del formulario antes de permitir la creación de sanes/rifas

### Manejo de Errores
- Validación robusta de tipos de datos
- Manejo de excepciones en cálculos
- Mensajes de error descriptivos
- Fallbacks para valores faltantes

### Interfaz de Usuario
- Diseño responsivo con Tailwind CSS
- Indicadores visuales claros (✅ para éxito, ⚠️ para advertencias)
- Tarjetas organizadas para mostrar métricas
- Colores consistentes (verde para viable, rojo para no viable)

## Uso

### Para Organizadores de Sanes:
1. Ir a "Crear San"
2. Llenar los campos del formulario
3. Ver los cálculos automáticos que aparecen debajo
4. Ajustar parámetros según las alertas mostradas
5. Crear el san cuando sea viable

### Para Organizadores de Rifas:
1. Ir a "Crear Rifa"
2. Llenar los campos del formulario
3. Ver los cálculos automáticos que aparecen debajo
4. Ajustar parámetros según las alertas mostradas
5. Crear la rifa cuando sea viable

## Beneficios

1. **Prevención de errores**: Los organizadores pueden ver inmediatamente si sus parámetros son viables
2. **Transparencia**: Cálculos claros y visibles para todos los participantes
3. **Eficiencia**: No es necesario hacer cálculos manuales
4. **Experiencia de usuario mejorada**: Feedback inmediato y visual
5. **Reducción de sanes/rifas fallidas**: Los organizadores pueden ajustar parámetros antes de crear
6. **Cálculos correctos**: La cuota por participante se calcula correctamente (monto_total / numero_cuotas)
7. **Validación robusta**: El sistema valida los datos antes de permitir la creación
8. **Actualización automática**: Los cálculos se ejecutan automáticamente al cargar la página y al modificar campos

## Pruebas

Se incluye un script de prueba (`test_calculations.py`) que verifica:
- Cálculos correctos para sanes viables
- Detección de sanes no viables
- Cálculos correctos para rifas viables
- Detección de rifas no viables
- Manejo de casos edge y errores

Para ejecutar las pruebas:
```bash
python test_calculations.py
```

## Notas de Implementación

- Los cálculos se realizan en el servidor para mayor seguridad
- Se usa AJAX para actualizaciones en tiempo real sin recargar la página
- Los formularios mantienen su funcionalidad original
- Se agregaron validaciones adicionales para evitar errores
- El código es compatible con la estructura existente del proyecto
