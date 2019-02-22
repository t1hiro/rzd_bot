import contextlib


def create_new_session(oper_id, subst_oper_id, database_id=None):
    # type: (Optional[PassportId], Optional[PassportId], Optional[DatabaseId]) -> Session
    """
    Creates new session authenticated with specified passport id.
    """
    LOGGER.debug(
        'Creating new session: oper_id=%s, subst_oper_id=%s, database_id=%s',
        oper_id,
        subst_oper_id,
        database_id,
    )

    yb_app = get_application()
    database_id_value = getattr(database_id, 'value', None)
    session = yb_app.new_session(oper_id, database_id=database_id_value)

    if subst_oper_id and session.check_perm(Permission.SUBSTITUTE_LOGIN, strict=False):
        LOGGER.debug('Substituting passport id with %s', subst_oper_id)

        session = yb_app.new_session(subst_oper_id, database_id=database_id_value)

    return session

@contextlib.contextmanager
def new_transactional_session():
    session = create_new_session(*get_auth())
    session.begin()

    try:
        yield session

        session.commit()
    except Exception:
        session.rollback()

        raise