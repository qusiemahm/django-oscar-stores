from django import template
register = template.Library()


def render_file_upload(field_name, label, help_text=None, form_prefix=None, has_error=False,tooltop_text=""):
    prefix = f"{form_prefix}-" if form_prefix else ""
   
    if tooltop_text:
        tooltip_icon = '''
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M11.6666 8.75033V8.33366C11.6666 7.41318 10.9205 6.66699 9.99998 6.66699C9.07951 6.66699 8.33331 7.41318 8.33331 8.33366V8.43476C8.33331 8.9036 8.51956 9.35324 8.85108 9.68476L9.99998 10.8337M9.58331 13.3337C9.58331 13.5638 9.76986 13.7503 9.99998 13.7503C10.2301 13.7503 10.4166 13.5638 10.4166 13.3337M9.58331 13.3337C9.58331 13.1035 9.76986 12.917 9.99998 12.917C10.2301 12.917 10.4166 13.1035 10.4166 13.3337M9.58331 13.3337H10.4166M1.66665 10.0003C1.66665 14.6027 5.39761 18.3337 9.99998 18.3337C14.6024 18.3337 18.3333 14.6027 18.3333 10.0003C18.3333 5.39795 14.6024 1.66699 9.99998 1.66699C5.39761 1.66699 1.66665 5.39795 1.66665 10.0003Z" stroke="#8083A3" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        '''
    else:
        
        tooltip_icon=""
    upload_icon = '''
    <svg width="29" height="28" viewBox="0 0 29 28" fill="none" xmlns="http://www.w3.org/2000/svg">
        <g clip-path="url(#clip0_1460_8857)">
            <path d="M3.8633 20.9997C2.32894 20.1072 1.29663 18.439 1.29663 16.5283C1.29663 14.1226 2.93329 12.1012 5.14805 11.5286C5.14711 11.4747 5.14663 11.4206 5.14663 11.3664C5.14663 6.37739 9.16861 2.33301 14.13 2.33301C18.3546 2.33301 21.8981 5.2654 22.8573 9.21644C25.2594 10.1491 26.9633 12.4934 26.9633 15.2378C26.9633 17.3488 25.9552 19.2231 24.3966 20.4002" stroke="#0000FF" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M14.1298 25.667L14.1298 15.167M14.1298 15.167L10.0465 19.2503M14.1298 15.167L18.2131 19.2503" stroke="#0000FF" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"/>
        </g>
        <defs>
            <clipPath id="clip0_1460_8857">
                <rect width="28" height="28" fill="white" transform="translate(0.129883)"/>
            </clipPath>
        </defs>
    </svg>
    '''
    
    border_color = 'border-danger' if has_error else 'border-primary'
    help_text_html = f'<small class="text-muted d-block mt-1">{help_text}</small>' if help_text else ''
    label_color =  ''
   
    return f'''
        <div class="form-group col-12 mb-3 file-upload-container">
            <label class="form-label w-100 cursor-pointer {label_color}" for="id_{prefix}{field_name}">
                <span class="icon-wrapper" data-bs-toggle="tooltip" data-bs-placement="right" title="{tooltop_text}">
                    {label} {tooltip_icon}
                </span>
                <div class="position-relative p-1 pt-2">
                    <div class="d-flex align-items-center justify-content-between gap-2 border border-2 {border_color} rounded p-4 text-center upload-area"
                         style="border-style: dashed !important;">
                        <div class="d-flex gap-2 justify-content-end align-items-center">
                            {upload_icon}
                            <span class="file-upload-text">
                                اختر ملفًا أو اسحبه وأفلته هنا
                            </span>
                        </div>
                        <span type="button" class="btn file-upload-btn btn-sm p-2">
                            رفع الملف
                        </span>
                    </div>
                    <div class="position-absolute top-0 start-0 w-100 h-100" style="opacity: 0">
                        <input type="file" name="{prefix}{field_name}" id="id_{prefix}{field_name}" class="form-control h-100">
                    </div>
                    {help_text_html}
                </div>
            </label>
        </div>
    '''
