"""US-16 · Aceptar una oferta."""
import threading

import pymysql
import pytest


@pytest.fixture
def oferta(crear_usuario, crear_oferta):
    return crear_oferta(crear_usuario("ana@example.com"), direccion="Calle Secreta 999")


def test_ca1_al_aceptar_queda_asignada_a_mi(entrar_como, post, consultar, oferta):
    recolector, recolector_id = entrar_como("recolector")
    respuesta = post(recolector, f"/recolector/ofertas/{oferta}/aceptar")
    assert respuesta.status_code == 302
    fila = consultar("SELECT estado, recolector_id FROM ofertas WHERE id = %s", (oferta,), uno=True)
    assert fila == {"estado": "Aceptada", "recolector_id": recolector_id}


def test_ca2_tras_aceptar_veo_la_direccion_exacta(entrar_como, post, oferta):
    recolector, _ = entrar_como("recolector")
    respuesta = post(recolector, f"/recolector/ofertas/{oferta}/aceptar", follow_redirects=True)
    assert "Calle Secreta 999" in respuesta.get_data(as_text=True)


def test_ca3_oferta_ya_tomada_no_se_reasigna(entrar_como, post, consultar, oferta):
    primero, primero_id = entrar_como("recolector")
    segundo, _ = entrar_como("recolector")
    post(primero, f"/recolector/ofertas/{oferta}/aceptar")
    respuesta = post(segundo, f"/recolector/ofertas/{oferta}/aceptar", follow_redirects=True)
    assert "ya no está disponible" in respuesta.get_data(as_text=True)
    assert consultar("SELECT recolector_id FROM ofertas WHERE id = %s", (oferta,), uno=True)["recolector_id"] == primero_id


def test_ca4_aceptacion_simultanea_solo_uno_la_obtiene(app, crear_usuario, oferta):
    from app.blueprints.recolector import intentar_aceptar
    recolectores = [crear_usuario(f"r{i}@example.com", rol="recolector") for i in (1, 2)]
    barrera, resultados = threading.Barrier(2), []

    def intentar(recolector_id):
        c = app.config
        conexion = pymysql.connect(host=c["DB_HOST"], port=c["DB_PORT"], user=c["DB_USER"], password=c["DB_PASSWORD"],
                                   database=c["DB_NAME"], autocommit=True)
        try:
            barrera.wait()
            resultados.append(intentar_aceptar(conexion, oferta, recolector_id, "Miraflores"))
        finally:
            conexion.close()

    hilos = [threading.Thread(target=intentar, args=(r,)) for r in recolectores]
    for hilo in hilos:
        hilo.start()
    for hilo in hilos:
        hilo.join()
    assert sorted(resultados) == [False, True]


def test_otro_recolector_no_ve_el_detalle(entrar_como, post, oferta):
    primero, _ = entrar_como("recolector")
    segundo, _ = entrar_como("recolector")
    post(primero, f"/recolector/ofertas/{oferta}/aceptar")
    assert segundo.get(f"/recolector/ofertas/{oferta}").status_code == 403
