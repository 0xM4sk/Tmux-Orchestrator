|
from flask import render_template, redirect, url_for, flash
from .forms.profile_form import ProfileForm

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
form = ProfileForm()

if form.validate_on_submit():
current_user.profile.bio = form.bio.data
current_user.profile.profile_picture_url = form.profile_picture_url.data
db.session.commit()
flash('Your profile has been updated!', 'success')
return redirect(url_for('main.home'))

elif request.method == 'GET':
form.bio.data = current_user.profile.bio
form.profile_picture_url.data = current_user.profile.profile_picture_url

return render_template('edit_profile.html', title='Edit Profile', form=form)