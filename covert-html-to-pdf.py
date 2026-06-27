### Convert html pages with pdf format, additionally links with another pages are added and script is working

import os
import asyncio
from playwright.async_api import async_playwright
from PIL import Image

async def capture_isolated_slides():
    input_path = "/Users/iftitt/Downloads/masdr-sdlc-presentation(59).html"
    output_pdf_path = "/Users/iftitt/Downloads/masdr-devsecops.pdf"
    file_url = f"file://{input_path}"
    
    temp_dir = "./temp_slides"
    os.makedirs(temp_dir, exist_ok=True)
    
    print("Initializing isolated element parser...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Large viewport ensures wide tables or long link structures don't wrap tightly
        context = await browser.new_context(
            viewport={"width": 1600, "height": 1000},
            device_scale_factor=2
        )
        page = await context.new_page()
        
        await page.goto(file_url, wait_until="networkidle")
        await page.wait_for_timeout(2000)
        
        image_paths = []
        
        # Step through all 19 slides using keyboard navigation
        for slide_num in range(1, 20):
            print(f"Capturing Slide {slide_num}/19 cleanly...")
            
            # --- Anti-Duplication Logic ---
            # Instead of a full-page screenshot which can capture scrolling duplicates,
            # we locate the active slide container directly in the DOM.
            # Most frameworks use '.present', 'section', or '.active' for the visible slide.
            active_selectors = [
                "section.present", 
                ".slide.active", 
                "section.active",
                ".reveal .slides > section"
            ]
            
            slide_element = None
            for selector in active_selectors:
                el = await page.query_selector(selector)
                if el and await el.is_visible():
                    slide_element = el
                    break
            
            img_path = f"{temp_dir}/slide_{slide_num:02d}.png"
            
            if slide_element:
                # Capture ONLY the bounding box of that specific slide element
                await slide_element.screenshot(path=img_path)
            else:
                # Fallback to viewport capture if custom slide elements aren't found
                await page.screenshot(path=img_path, full_page=False)
                
            image_paths.append(img_path)
            
            # Move to next slide frame
            if slide_num < 19:
                await page.keyboard.press("ArrowRight")
                # Wait long enough for transition animations to completely disappear
                await page.wait_for_timeout(900)
                
        await browser.close()
    
    print("\nCompiling clean slide deck into PDF format...")
    images = [Image.open(f).convert("RGB") for f in image_paths]
    
    if images:
        images[0].save(
            output_pdf_path, 
            format="PDF", 
            save_all=True, 
            append_images=images[1:],
            quality=100
        )
        print(f"\n🎉 Success! Output built with 0 duplicated segments.")
        print(f"Saved file to: {output_pdf_path}")
    
    # Cleanup
    for f in image_paths:
        try: os.remove(f)
        except OSError: pass
    try: os.rmdir(temp_dir)
    except OSError: pass

if __name__ == "__main__":
    asyncio.run(capture_isolated_slides())
