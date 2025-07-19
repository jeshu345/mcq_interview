from flask import Blueprint
from ..views import admin_views

admin_bp = Blueprint('admin_bp', __name__) # Removed url_prefix here, it's in app.register_blueprint




admin_bp.add_url_rule(
    "/register",
    view_func=admin_views.RegisterAdmin.as_view("register_admin_api"),
    methods=["POST"]
)

admin_bp.add_url_rule(
    "/adminlogin",
    view_func=admin_views.AdminLoginAPI.as_view("admin_login_api"),
    methods=["POST"]
)

admin_bp.add_url_rule(
    "/forgotpassword",
    view_func=admin_views.ForgotPasswordAPI.as_view("admin_forgot_password"),
    methods=["POST"]
)

admin_bp.add_url_rule(
    "/otpVerified",
    view_func=admin_views.VerifyOTP.as_view("otp_verified"),
    methods=["POST"]
    )

admin_bp.add_url_rule(
    "/resend_otp",
    view_func=admin_views.ResendOTPAPI.as_view("resend_otp"),
    methods=["POST"]

)

admin_bp.add_url_rule(
    "/changepassword",
    view_func=admin_views.ChangePassword.as_view("change_password"),
    methods=['POST']
)

admin_bp.add_url_rule(
    "/new_password",  # Route for changing password when logged in
    view_func=admin_views.NewPassword.as_view("new_password"),
    methods=['POST']
)

admin_bp.add_url_rule(
    "/update_profile",
    view_func=admin_views.UpdateAdminProfile.as_view("update_profile"),
    methods=['PUT']
)

admin_bp.add_url_rule(
    "/get/all/admins_details",
    view_func=admin_views.GetAllAdmins.as_view("get_details"),
    methods=['GET']
)


admin_bp.add_url_rule(
    "/get/admins_details/<admin_id>",
    view_func=admin_views.GetAdminByObjectId.as_view("get_admin"),
    methods=['GET']
)

admin_bp.add_url_rule(
    "/create/batch",  # Route for changing password when logged in
    view_func=admin_views.CreateBatch.as_view("create_batch"),
    methods=['POST']
)

admin_bp.add_url_rule(
    "/get_details/<batch_id>",  # Route for changing password when logged in
    view_func=admin_views.GetBatchCandidates.as_view("get_batch_candidates"),
    methods=['GET']
)

admin_bp.add_url_rule(
    "/assign/batch/<batch_id>",  # Route for changing password when logged in
    view_func=admin_views.AssignMCQsToBatch.as_view("assign_mcqs_to_batch"),
    methods=['POST']
)

admin_bp.add_url_rule(
    "/results/<batch_id>",  # Route for changing password when logged in
    view_func=admin_views.AdminGetResults.as_view("admin_get_results"),
    methods=['GET']
)