import os
from os.path import join as join_paths
from contextlib import contextmanager
import uuid
import shutil
import fnmatch


import logging
log = logging.getLogger(__name__)


def mk_dir_recursive(dir_path):
    if os.path.isdir(dir_path):
        return
    h, t = os.path.split(dir_path)  # head/tail
    if not os.path.isdir(h):
        mk_dir_recursive(h)

    new_path = join_paths(h, t)
    if not os.path.isdir(new_path):
        os.mkdir(new_path)


def zaluz_katalog(katalog):
    if not os.path.isdir(katalog):
        os.makedirs(katalog)
    return katalog


def py_mk_dir_recursive(dir_path):
    if os.path.isdir(dir_path):
        return
    h, t = os.path.split(dir_path)  # head/tail
    if not os.path.isdir(h):
        py_mk_dir_recursive(h)

    new_path = join_paths(h, t)
    if not os.path.isdir(new_path):
        os.mkdir(new_path)
        with open(os.path.join(new_path, "__init__.py"), "w") as f:
            f.write(u"# -*- coding: utf-8 -*-")


@contextmanager
def ctx_tmp_dir(usun=True):
    uid = uuid.uuid4()
    katalog = "/tmp/{}".format(uid.hex)
    log.debug('Create temp dir: %s', katalog)
    katalog = zaluz_katalog(katalog)
    try:
        yield katalog
    finally:
        if usun:
            try:
                shutil.rmtree(katalog)
                log.debug(u"Delete temp dir: %r", katalog)
            except Exception:
                log.warn(u"Can't remove temp dir %r", katalog, exc_info=True)
        else:
            log.info(u"Pomijam usunięcie katalogu: %r", katalog)


def rm_r(self, path):
    if os.path.isdir(path) and not os.path.islink(path):
        shutil.rmtree(path)
    elif os.path.exists(path):
        os.remove(path)


def gen_rec_list_file(self, sciezka, pattern=u"*"):
    for dirpath, dirnames, filenames in os.walk(sciezka):
        for file_name in fnmatch.filter(filenames, pattern):
            yield os.path.join(dirpath, file_name)


def utworz_tmp_plik(tmp_dir, tresc_bin):
    u'''
    Funkcja tworzy plik o unikalnej losowej nazwie w podanym `tmp_dir` i zwraca do niego ścieżkę.
    Plik nie jest usuwany automatycznie - rekomendowane jest użycie wraz z contextmanager'em `ctx_tmp_dir`
    '''
    nazwa_pliku = uuid.uuid4()
    sciezka_do_pliku = os.path.join(tmp_dir, nazwa_pliku.hex)
    with open(sciezka_do_pliku, 'wb') as f:
        # f.write(tresc_bin)
        f.write(tresc_bin)
    return sciezka_do_pliku
