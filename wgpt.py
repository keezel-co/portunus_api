from wgpt import app, db

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Voucher': Voucher, 'UserVoucher': UserVoucher}

