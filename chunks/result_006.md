Việc ánh xạ các Subdomains (Miền con) theo tỷ lệ một-đối-một với các Bounded Contexts (Ngữ cảnh Giới hạn) là một mục tiêu rất đáng mong đợi. Làm được điều đó sẽ phân tách rạch ròi các domain models (mô hình miền) thành các khu vực nghiệp vụ được xác định rõ ràng theo từng mục tiêu, hợp nhất không gian bài toán (problem space) với không gian giải pháp (solution space). Trong thực tế, điều này không phải lúc nào cũng khả thi, nhưng nó hoàn toàn có thể hiệu quả trong một dự án phát triển mới hoàn toàn trên bãi đất trống (greenfield effort). Tuy nhiên, khi xét đến một hệ thống cũ (legacy system), và rất có thể là một Big Ball of Mud (Kiến trúc Búi bùn lớn), các Subdomains thường giao thoa và cắt ngang qua nhiều Bounded Contexts, tương tự như những gì chúng ta đã thảo luận liên quan đến Hình 2.1. Trong một doanh nghiệp quy mô lớn và phức tạp, chúng ta có thể áp dụng một góc nhìn đánh giá (assessment view) để thấu hiểu không gian bài toán của mình, điều này có thể cứu chúng ta khỏi những sai lầm vô cùng tốn kém. Chúng ta có thể chia tách một Bounded Context đơn lẻ có quy mô lớn về mặt khái niệm bằng cách sử dụng hai hoặc nhiều Subdomains, hoặc gộp nhiều Bounded Contexts thành một phần của một Subdomain duy nhất. Hãy xem xét một ví dụ để làm sáng tỏ sự khác biệt giữa không gian bài toán và không gian giải pháp.

Hãy hình dung một hệ thống nguyên khối (monolithic system) đồ sộ, được phân loại là một ứng dụng ERP (Enterprise Resource Planning - Hệ thống Hoạch định Nguồn lực Doanh nghiệp). Theo nghĩa hẹp, một hệ thống ERP có thể được coi là một Bounded Context đơn lẻ. Tuy nhiên, vì các hệ thống ERP cung cấp rất nhiều dịch vụ nghiệp vụ dạng module, sẽ có lợi nếu chúng ta tư duy về các module khác biệt như những Subdomains riêng biệt. Chẳng hạn, chúng ta có thể chia module quản lý kho và module mua hàng thành các Subdomains logic riêng biệt. Đúng là các module này không được cung cấp thông qua các hệ thống hoàn toàn khác nhau. Cả hai đều là một phần của cùng một hệ thống ERP. Dẫu vậy, mỗi module lại mang đến một tập hợp dịch vụ rất khác biệt cho miền nghiệp vụ. Phục vụ cho các cuộc thảo luận mang tính phân tích, hãy đặt tên cho chúng thành các Subdomains riêng biệt: Inventory Subdomain (Miền con Quản lý Kho) và Purchasing Subdomain (Miền con Mua hàng). Tiếp tục với ví dụ này, chúng ta sẽ thấy lý do tại sao việc làm đó lại hữu ích.

Với tư cách là một sáng kiến kinh doanh cốt lõi, tổ chức có Domain được biểu diễn trong Hình 2.4 (một ví dụ cụ thể sử dụng mẫu từ Hình 2.2) bắt đầu lập kế hoạch thiết kế và phát triển một domain model chuyên biệt nhằm cắt giảm chi phí vận hành kinh doanh. Mô hình này sẽ cung cấp các công cụ hỗ trợ ra quyết định dành cho các nhân viên thu mua. Các thuật toán vốn được đúc kết qua nhiều năm vận hành quy trình thủ công bởi con người giờ đây bắt buộc phải được tự động hóa bằng phần mềm để đảm bảo chúng luôn được mọi nhân viên thu mua áp dụng chuẩn xác mà không xảy ra sai sót. Core Domain (Miền cốt lõi) mới này sẽ giúp tổ chức nâng cao năng lực cạnh tranh bằng cách nhận diện các thương vụ tốt hơn một cách nhanh chóng hơn, rồi sau đó đảm bảo đáp ứng đầy đủ lượng hàng tồn kho cần thiết. Để nhập hàng tồn kho một cách chuẩn xác, việc sử dụng Forecasting System (Hệ thống Dự báo) đã được khảo sát trước đó trong Hình 2.1 cũng sẽ hỗ trợ đắc lực tại đây.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000039_b056d0d187b29e3dea8f41065004d45d5e2a7f1adc81d9c26343f869f17c5ab6.png)

Figure 2.4 Core Domain và các Subdomains khác liên quan đến việc mua hàng và quản lý kho. Góc nhìn này được giới hạn trong các Subdomains được chọn lọc phục vụ cho việc phân tích không gian bài toán cụ thể, chứ không đại diện cho toàn bộ Domain.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000040_f54e6e5a48d6ab6c7be872735719513c34d77df89280474621dc93b0b8d2a2a7.png)

Trước khi có thể triển khai một giải pháp cụ thể, chúng ta cần thực hiện đánh giá không gian bài toán và không gian giải pháp. Dưới đây là một số câu hỏi cần được giải đáp nhằm chèo lái dự án của bạn đi đúng hướng:

- Tên gọi và tầm nhìn dành cho Core Domain mang tính chiến lược là gì?
- Những khái niệm nào nên được coi là một phần của Core Domain chiến lược?
- Đâu là các Supporting Subdomains (Miền con Hỗ trợ) và Generic Subdomains (Miền con Chung) cần thiết?
- Ai nên đảm nhận công việc trong từng khu vực của miền?
- Liệu có thể quy tụ được các đội ngũ phù hợp hay không?

Nếu chúng ta không thấu hiểu tầm nhìn và mục tiêu của Core Domain cùng các khu vực của Domain cần thiết để hỗ trợ nó, chúng ta sẽ không thể tận dụng chúng một cách chiến lược và tránh khỏi những cạm bẫy liên quan. Hãy giữ cho việc đánh giá không gian bài toán ở mức khái quát cấp cao, nhưng phải đảm bảo tính thấu đáo. Hãy chắc chắn rằng tất cả các bên liên quan (stakeholders) đều đồng thuận và cam kết hiện thực hóa thành công tầm nhìn đó.

## Giờ Làm việc với Bảng trắng (Whiteboard Time)

Hãy dành chút thời gian nhìn lại những gì bạn đã vẽ trên bảng trắng và cân nhắc: Không gian bài toán của bạn là gì? Hãy nhớ lại rằng đó là sự kết hợp giữa Core Domain mang tính chiến lược và các Subdomains hỗ trợ nó.

Khi bạn đã có được sự thấu hiểu rõ ràng về không gian bài toán, bạn sẽ chuyển hướng sang không gian giải pháp. Đợt đánh giá đầu tiên sẽ cung cấp tri thức cho đợt đánh giá thứ hai. Không gian giải pháp sẽ chịu ảnh hưởng mạnh mẽ từ các hệ thống và công nghệ hiện có, cũng như những thứ sắp sửa được tạo mới. Tại đây chúng ta thực sự cần tư duy dưới góc độ của các Bounded Contexts được phân tách rạch ròi, bởi vì chúng ta đang xem xét Ubiquitous Language (Ngôn ngữ Chung / Toàn hiện) của từng ngữ cảnh. Hãy cân nhắc những câu hỏi then chốt sau:

- Những tài sản phần mềm nào đã tồn tại sẵn, và liệu chúng có thể tái sử dụng được không?
- Những tài sản nào cần phải mua ngoài hoặc tự phát triển mới?
- Tất cả những thành phần này kết nối với nhau, hay tích hợp với nhau như thế nào?
- Những tích hợp bổ sung nào sẽ là cần thiết?
- Xét trên các tài sản sẵn có và những tài sản cần tạo mới, mức độ nỗ lực đòi hỏi là bao nhiêu?
- Liệu sáng kiến chiến lược và toàn bộ các dự án hỗ trợ có xác suất thành công cao hay không, hoặc liệu có bất kỳ dự án đơn lẻ nào trong số đó có nguy cơ khiến toàn bộ chương trình bị chậm tiến độ hay thậm chí sụp đổ không?
- Đâu là nơi mà các thuật ngữ của các Ubiquitous Languages liên quan hoàn toàn khác biệt nhau?
- Đâu là nơi có sự chồng chéo và chia sẻ khái niệm cũng như dữ liệu giữa các Bounded Contexts?
- Các thuật ngữ dùng chung và/hoặc các khái niệm chồng chéo được ánh xạ và phiên dịch giữa các Bounded Contexts như thế nào?
- Bounded Context nào chứa đựng các khái niệm giải quyết Core Domain và những mẫu hình chiến thuật nào của [Evans] sẽ được sử dụng để mô hình hóa nó?

Hãy nhớ rằng, những nỗ lực trong việc phát triển các giải pháp thuộc Core Domain chính là một khoản đầu tư kinh doanh then chốt!

Mô hình mua hàng chuyên biệt được mô tả trước đó và được minh họa trong Hình 2.4 — mô hình nắm bắt các công cụ và thuật toán hỗ trợ ra quyết định — đại diện cho giải pháp dành cho Core Domain. Mô hình miền này sẽ được triển khai trong một Bounded Context tường minh: Optimal Acquisitions Context (Ngữ cảnh Thu mua Tối ưu). Bounded Context này ăn khớp một-đối-một với Subdomain Optimal Acquisitions Core Domain. Việc được căn chỉnh với chỉ duy nhất một Subdomain, cùng với mô hình miền được gia công tỉ mỉ, sẽ biến nó thành một trong những Bounded Contexts xuất sắc nhất trong miền kinh doanh này.

Một Bounded Context khác, Purchasing Context (Ngữ cảnh Mua hàng), sẽ được phát triển nhằm tinh chỉnh một số khía cạnh kỹ thuật của quy trình mua hàng với vai trò là một thành phần trợ lực cho Optimal Acquisitions Context. Những tinh chỉnh này không bộc lộ bất kỳ tri thức đặc biệt nào về một phương pháp tiếp cận thu mua tối ưu. Chúng chỉ đơn giản giúp cho Optimal Acquisitions Context tương tác với hệ thống ERP một cách độc lập và giữ khoảng cách an toàn (at an arm's length). Đó chỉ là một mô hình tiện ích hoạt động dựa trên giao diện công khai (published interface) của hệ thống ERP. Purchasing Context mới cùng với module mua hàng sẵn có của ERP nằm trong Purchasing (Supporting) Subdomain.

Module mua hàng của ERP xét về tổng thể là một Generic Subdomain. Đó là vì bạn hoàn toàn có thể thay thế Subdomain này bằng bất kỳ hệ thống mua hàng thương mại đóng gói sẵn (off-the-shelf) nào, miễn là nó đáp ứng được các nhu cầu kinh doanh cơ bản của bạn. Tuy nhiên, việc được sử dụng song hành cùng với Purchasing Context mới bên trong Purchasing Subdomain lại khiến nó vận hành theo phương thức Hỗ trợ (Supporting).

> 💡 **Giải thích thêm:** Thành ngữ "at an arm's length" (cự ly một cánh tay / khoảng cách an toàn) vốn bắt nguồn từ thuật ngữ pháp lý và thương mại chỉ mối quan hệ giữa hai bên độc lập, sòng phẳng và không bị chi phối lẫn nhau. Trong kiến trúc phần mềm, tương tác "at an arm's length" chỉ việc hệ thống giao tiếp với một dịch vụ bên ngoài (như ERP) thông qua một lớp trung gian cách ly, giữ khoảng cách độc lập để sự thay đổi nội bộ của ERP không làm xáo trộn hay ô nhiễm mô hình miền cốt lõi.
> Nguồn tham khảo: (Không có nguồn trích dẫn xác thực — cần tự kiểm chứng thêm)

## Bạn Không thể Thay đổi Thế giới của Thiết kế Phần mềm Tồi tệ (You Can't Change the World of Bad Software Design)

Trong một doanh nghiệp cải tạo trên nền tảng sẵn có (brownfield enterprise) điển hình, bạn chắc chắn sẽ gặp phải những tình huống không mong muốn như được minh họa trong Hình 2.1 và Hình 2.4. Điều này có nghĩa là các Subdomains trong phần mềm được thiết kế tồi tệ sẽ không ăn khớp theo cách thức lý tưởng một-đối-một với các Bounded Contexts. Bạn không thể thay đổi cả thế giới của thiết kế phần mềm tồi tệ. Bạn chỉ có thể hy vọng triển khai DDD chuẩn mực trong các dự án mà mình trực tiếp tham gia. Sau cùng, bạn vẫn sẽ phải tích hợp với và thậm chí làm việc bên trong các miền brownfield, vì vậy hãy chuẩn bị sẵn sàng để vận dụng các kỹ thuật được giảng dạy trong một phần ba đầu tiên của chương này khi bạn phân tích nhiều mô hình ngầm định ẩn chứa bên trong một Bounded Context đơn lẻ, chắp vá cũ kỹ.

Vẫn bám sát Hình 2.4, Optimal Acquisition Context cũng bắt buộc phải tương tác với Inventory Context. Inventory quản lý các mặt hàng lưu kho. Nó sử dụng module quản lý kho của ERP — module vốn thuộc về Inventory (Supporting) Subdomain. Để tạo sự thuận tiện cho các nhà thầu giao hàng, Inventory Context có thể cung cấp bản đồ và chỉ đường đến từng nhà kho của mình từ một địa điểm xuất phát bằng cách sử dụng một dịch vụ bản đồ địa lý bên ngoài (external geographical mapping service). Từ góc nhìn của Inventory Context, dịch vụ bản đồ chẳng có gì đặc biệt. Có rất nhiều dịch vụ bản đồ địa lý để lựa chọn, và có thể có những lợi ích nhất định khi thay đổi hệ thống bản đồ được chọn theo thời gian. Bản thân dịch vụ bản đồ là một Generic Subdomain, nhưng nó lại được tiêu thụ bởi một Supporting Subdomain.

Hãy lưu ý những điểm mấu chốt này khi được quan sát từ lăng kính của công ty đang phát triển Optimal Acquisition Context: Trong không gian giải pháp, dịch vụ bản đồ địa lý không phải là một phần của Inventory Context, mặc dù trong không gian bài toán nó được coi là một phần của Inventory Subdomain. Trong không gian giải pháp, ngay cả khi các dịch vụ bản đồ được cung cấp thông qua một API (Application Programming Interface - Giao diện Lập trình Ứng dụng) dựa trên thành phần đơn giản, nó vẫn nằm trong một Bounded Context khác biệt. Ubiquitous Language của Quản lý kho (Inventory) và của Bản đồ (Mapping) hoàn toàn loại trừ lẫn nhau, đồng nghĩa với việc chúng nằm trong các Bounded Contexts khác nhau. Khi Inventory Context sử dụng một thành phần nào đó từ Mapping Context bên ngoài, dữ liệu có thể phải trải qua ít nhất một sự phiên dịch tối thiểu để có thể được tiêu thụ một cách chuẩn xác.

Mặt khác, xét từ góc nhìn của tổ chức kinh doanh bên ngoài chuyên phát triển và cung cấp dịch vụ bản đồ dưới dạng thuê bao, lập bản đồ lại chính là một Core Domain. Tổ chức bên ngoài đó có domain riêng, hay lãnh địa vận hành kinh doanh của riêng họ. Họ bắt buộc phải duy trì năng lực cạnh tranh, không ngừng tinh chỉnh domain model của mình nhằm giữ chân các thuê bao hiện tại và thu hút thêm những khách hàng mới. Nếu bạn là CEO của tổ chức cung cấp dịch vụ bản đồ đó, bạn sẽ đảm bảo mang lại cho khách hàng — bao gồm cả khách hàng thuê bao đơn lẻ đang được thảo luận ở đây — mọi lý do xác đáng để tiếp tục gắn bó với dịch vụ của bạn thay vì chuyển sang đối thủ cạnh tranh. Tuy nhiên, điều đó không làm thay đổi góc nhìn của bên thuê bao vốn đang phát triển hệ thống quản lý kho của riêng mình. Đối với hệ thống kho, đó vẫn chỉ là một Generic Subdomain. Họ hoàn toàn có thể chuyển sang đăng ký một dịch vụ bản đồ khác nếu điều đó mang lại lợi thế cho họ.

## Giờ Làm việc với Bảng trắng (Whiteboard Time)

Đâu là các Bounded Contexts trong không gian giải pháp của bạn? Tại thời điểm này, bạn có thể tham chiếu lại sơ đồ trên bảng trắng của mình để có được một hình dung tốt. Dẫu vậy, bạn có thể sẽ cảm thấy đôi chút bất ngờ khi chúng ta đào sâu hơn vào cách thức sử dụng Bounded Contexts chuẩn mực. Vì vậy, hãy sẵn sàng cho những sự tinh chỉnh có thể xảy ra. Xét cho cùng, chúng ta đang thực hành phát triển linh hoạt (agile).

Như vậy, trong phần còn lại của chương này, chúng ta sẽ chuyển hướng và xem xét tầm quan trọng của Bounded Contexts với tư cách là một công cụ mô hình hóa không gian giải pháp thiết yếu cho DDD. Trong chương Context Maps (3), cuộc thảo luận chủ yếu nhấn mạnh cách xử lý việc ánh xạ giữa các Ubiquitous Languages khác nhau nhưng có liên quan mật thiết, bằng cách tích hợp các Bounded Contexts của chúng lại với nhau.

## Hiểu đúng về Bounded Contexts (Making Sense of Bounded Contexts)

Đừng quên rằng, một Bounded Context là một ranh giới tường minh mà bên trong đó một domain model tồn tại. Domain model biểu đạt một Ubiquitous Language dưới dạng một mô hình phần mềm. Ranh giới này được tạo ra bởi vì mỗi khái niệm bên trong mô hình, cùng với các thuộc tính và thao tác của nó, đều mang một ý nghĩa đặc thù. Nếu bạn là thành viên của một đội ngũ mô hình hóa như vậy, bạn sẽ hiểu chính xác ý nghĩa của từng khái niệm trong Context của mình.

## Bounded Context Mang tính Tường minh và Ngôn ngữ (Bounded Context Is Explicit and Linguistic)

Một Bounded Context là một ranh giới tường minh mà bên trong đó một domain model tồn tại. Bên trong ranh giới đó, mọi thuật ngữ và cụm từ của Ubiquitous Language đều mang ý nghĩa cụ thể, và mô hình phản ánh Ngôn ngữ đó với độ chính xác tuyệt đối.

Thường xuyên xảy ra trường hợp trong hai mô hình khác biệt rõ ràng, các đối tượng có tên gọi giống hệt hoặc tương tự nhau lại mang những ý nghĩa hoàn toàn khác nhau. Khi một ranh giới tường minh được thiết lập bao quanh riêng từng mô hình trong số hai mô hình đó, ý nghĩa của mỗi khái niệm trong từng Context sẽ được xác định chắc chắn. Do đó, một Bounded Context về căn bản là một ranh giới về mặt ngôn ngữ (linguistic boundary). Bạn nên sử dụng những lập luận này làm tiêu chuẩn đối chiếu để xác định xem liệu mình có đang sử dụng Bounded Contexts đúng cách hay không.

Một số dự án rơi vào cái bẫy cố gắng tạo ra một mô hình bao quát tất cả, nơi mục tiêu là khiến toàn bộ tổ chức phải đồng thuận về các khái niệm có tên gọi chỉ mang duy nhất một ý nghĩa toàn cục (global meaning). Tiếp cận nỗ lực mô hình hóa theo cách này là một cạm bẫy chết người. Trước hết, gần như bất khả thi để thiết lập sự đồng thuận giữa tất cả các bên liên quan rằng mọi khái niệm đều mang một ý nghĩa toàn cục duy nhất, thuần khiết và khác biệt. Một số tổ chức lớn và phức tạp đến mức bạn sẽ không bao giờ có thể quy tụ tất cả các bên liên quan lại với nhau, chứ đừng nói đến việc thiết lập sự đồng thuận hoàn toàn và có ý nghĩa giữa họ. Ngay cả khi bạn làm việc trong một công ty nhỏ hơn với tương đối ít bên liên quan, việc thiết lập một định nghĩa bền vững cho một khái niệm toàn cục duy nhất vẫn là điều khó xảy ra. Vì vậy, lập trường tốt nhất nên theo đuổi là chấp nhận thực tế rằng sự khác biệt luôn luôn tồn tại, và hãy áp dụng Bounded Context để phân định tách biệt từng domain model — nơi mà những khác biệt được thể hiện tường minh và được thấu hiểu trọn vẹn.

Một Bounded Context không áp đặt việc phải tạo ra một loại tạo tác dự án (project artifact) đơn lẻ cụ thể nào. Nó không phải là một thành phần, một tài liệu hay một biểu đồ riêng lẻ. [^3] Do đó, nó không phải là một file JAR hay DLL, nhưng những file này có thể được sử dụng để triển khai (deploy) một Bounded Context như được mô tả ở phần sau của chương.

Hãy xem xét sự tương phản sâu sắc giữa khái niệm Account (Tài khoản) trong một Banking Context (Ngữ cảnh Ngân hàng) và Account (Lời thuật lại / Lời kể) trong một Literary Context (Ngữ cảnh Văn học) được trình bày trong Bảng 2.1.

[^3]: Bạn có thể vẽ biểu đồ của một hoặc nhiều Bounded Contexts như thấy ở đây và trong Context Maps. Tuy nhiên, bản thân biểu đồ đó không phải là Bounded Context.

Table 2.1 Sự Đa dạng về Ý nghĩa mà Thuật ngữ Account Có thể Sở hữu (The Diversity of Meanings That the Term Account Can Have)

| Context | Ý nghĩa | Ví dụ |
|---|---|---|
| Banking Context | Một Account duy trì bản ghi về các giao dịch ghi nợ và ghi có thể hiện trạng thái tài chính hiện tại của khách hàng với ngân hàng. | Checking Account (Tài khoản Vãng lai) và Savings Account (Tài khoản Tiết kiệm) |
| Literary Context | Một Account là một tập hợp các biểu đạt văn học về một hoặc nhiều sự kiện liên quan diễn ra trong một khoảng thời gian. | Amazon.com bán cuốn sách *Into Thin Air: A Personal Account of the Mt. Everest Disaster* (Tan vào Hư vô: Bản Tường thuật Cá nhân về Thảm họa Đỉnh Everest). |

Nhìn vào Hình 2.5, không có đặc điểm nhận diện nào trong tên gọi của các kiểu Account có thể giúp phân biệt chúng. Chỉ bằng cách nhìn vào tên gọi của từng vỏ chứa khái niệm — tức Bounded Context của nó — bạn mới hiểu được sự khác biệt giữa hai khái niệm này.

Hai Bounded Contexts này có thể không nằm trong cùng một Domain. Mục đích ở đây là nhằm chứng minh rằng ngữ cảnh là yếu tố tối thượng (context is king).

## Ngữ cảnh Là Vua (Context Is King)

Ngữ cảnh là vua, đặc biệt là khi triển khai DDD.

Trong giới tài chính, từ *security* (chứng khoán / bảo đảm) rất thường xuyên được sử dụng. Ủy ban Chứng khoán và Giao dịch Hoa Kỳ (SEC - Securities and Exchange Commission) giới hạn thuật ngữ *security* chỉ được dùng cho cổ phiếu (equities). Bây giờ hãy xem xét điều này: Các hợp đồng tương lai (Futures contracts) là hàng hóa phái sinh (commodities) và không thuộc quyền tài phán của SEC. Tuy nhiên, một số công ty tài chính vẫn gọi Hợp đồng Tương lai bằng cái tên *security* như một cách tham chiếu nhưng gắn nhãn cho chúng bằng Kiểu Tiêu chuẩn (Standard Type) (6) là *Futures*.

Liệu đó có phải là Ngôn ngữ chuẩn xác nhất cho một Future hay không? Điều đó phụ thuộc vào Domain mà nó được sử dụng bên trong. Một số người hiển nhiên sẽ khẳng định là có, trong khi những người khác lại kiên quyết cho rằng không. Ngữ cảnh cũng mang tính văn hóa (cultural). Bên trong một công ty cụ thể chuyên giao dịch Hợp đồng Tương lai, việc sử dụng thuật ngữ *Security* có thể hoàn toàn ăn khớp với văn hóa của họ bên trong một Ubiquitous Language cụ thể.

Figure 2.5 Các đối tượng Account trong hai Bounded Contexts khác nhau mang ý nghĩa hoàn toàn khác nhau, nhưng bạn chỉ biết được điều đó khi xem xét tên gọi của từng Bounded Context.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000041_7373b14fee785000b182488762ab64fe40489d392c9ca013cd85bd87b0013bf2.png)

Chính những ý nghĩa khác biệt tinh tế mới là thứ bạn thường xuyên phải đối mặt nhất trong doanh nghiệp của mình. Đây là lý do tại sao: Tên gọi được từng nhóm lựa chọn trong mỗi Context luôn luôn được đưa ra dựa trên sự cân nhắc về Ubiquitous Language. Bạn không bao giờ đặt tên cho một khái niệm một cách tùy tiện, chẳng hạn như cố tình làm cho nó khác biệt với một thuật ngữ trong một Context khác. Hãy xem xét hai Contexts ngân hàng: một cho tài khoản vãng lai (checking accounts) và một cho tài khoản tiết kiệm (savings accounts). [^4] Chúng ta không cần phải gán cái tên *Checking Account* cho đối tượng trong Checking Context hay cái tên *Savings Account* cho đối tượng trong Savings Context. Cả hai khái niệm đều có thể mang tên *Account* một cách an toàn bởi vì mỗi Bounded Context đã tự phân biệt những ý nghĩa tinh tế đó rồi. Đương nhiên, không có quy tắc nào cấm việc bổ sung thêm ý nghĩa cho những cái tên này. Đó là quyết định thuộc về đội ngũ của bạn.

[^4]: Điều này giả định một Domain nơi các Bounded Contexts riêng biệt được sử dụng cho tài khoản vãng lai và tài khoản tiết kiệm.

Khi phát sinh nhu cầu tích hợp, việc ánh xạ (mapping) bắt buộc phải được thực hiện giữa các Bounded Contexts. Đây có thể là một khía cạnh phức tạp của DDD và đòi hỏi một sự cẩn trọng tương xứng. Chúng ta thường không sử dụng một thể hiện đối tượng (object instance) bên ngoài ranh giới của nó, nhưng các đối tượng có liên quan trong nhiều ngữ cảnh khác nhau có thể chia sẻ một tập con trạng thái chung nào đó.

Dưới đây là một ví dụ khác về một tên gọi chung được sử dụng trong nhiều Bounded Contexts, nhưng lần này là bên trong cùng một Domain. Hãy xem xét những thách thức mô hình hóa của một tổ chức xuất bản phải xử lý các giai đoạn khác nhau trong vòng đời của những cuốn sách. Một cách khái quát, các nhà xuất bản xử lý các giai đoạn tương tự nhau khi một cuốn sách lần lượt đi qua các Contexts khác nhau:

- Khái niệm hóa và đề xuất bản thảo cuốn sách
- Ký hợp đồng với tác giả
- Quản lý quá trình chấp bút của tác giả và quy trình biên tập
- Thiết kế bố cục cuốn sách, bao gồm cả hình minh họa
- Dịch cuốn sách sang các ngôn ngữ khác
- Sản xuất các ấn bản in vật lý và/hoặc ấn bản điện tử
- Tiếp thị cuốn sách
- Bán sách cho các đại lý phân phối và/hoặc bán trực tiếp cho người tiêu dùng
- Giao sách vật lý tới các đại lý và người tiêu dùng

Xuyên suốt từng giai đoạn này, liệu có một cách thức duy nhất nào để mô hình hóa chuẩn xác một Book (Cuốn sách) hay không? Tuyệt đối không. Tại mỗi giai đoạn này, Book lại có những định nghĩa hoàn toàn khác biệt. Phải đến khi ký hợp đồng, Book mới có một tiêu đề dự kiến, và tiêu đề này hoàn toàn có thể thay đổi trong quá trình biên tập. Trong các giai đoạn viết sách và biên tập, Book sở hữu một tập hợp các bản thảo nháp kèm theo nhận xét và chỉnh sửa, cùng với một bản thảo cuối cùng. Các nhà thiết kế đồ họa tạo ra bố cục trang. Bộ phận sản xuất sử dụng bố cục đó để tạo ra các bản in thử kẽm, bản in thử định hình ("blue lines"), và cuối cùng là các bản kẽm in (plates). Bộ phận tiếp thị không cần đến hầu hết các tạo tác biên tập hay sản xuất đó, họ có thể chỉ cần bìa sách nghệ thuật và các mô tả cấp cao. Đối với khâu giao hàng, Book có thể chỉ mang một định danh (identity), vị trí trong kho, số lượng sẵn có, kích thước và trọng lượng.

> 💡 **Giải thích thêm:** "Blue lines" (bản in thử định hình / bản in xanh) là thuật ngữ truyền thống trong ngành in ấn và xuất bản sách. Đây là bản in thử nghiệm dùng giấy nhạy sáng màu xanh lam để biên tập viên và nhà in rà soát lần cuối toàn bộ vị trí văn bản, lề trang, hình ảnh trước khi khắc bản kẽm (plates) đưa vào dây chuyền in offset hàng loạt.
> Nguồn tham khảo: (Không có nguồn trích dẫn xác thực — cần tự kiểm chứng thêm)

Điều gì sẽ xảy ra nếu bạn cố gắng thiết kế một mô hình trung tâm duy nhất cho Book nhằm phục vụ cho tất cả các giai đoạn trong vòng đời của nó? Chắc chắn sẽ có sự nhầm lẫn, bất đồng và tranh cãi ở mức độ rất cao, và hầu như chẳng có phần mềm nào có thể bàn giao được. Ngay cả khi một mô hình chung đúng đắn có thể được tạo ra vào một thời điểm nào đó, nó rất có thể sẽ chỉ đáp ứng được nhu cầu của tất cả các bên một cách hiếm hoi và vô cùng ngắn ngủi.

Để ngăn chặn tình trạng cày xới liên miên mà không mang lại kết quả (churn and burn) không mong muốn đó, một nhà xuất bản mô hình hóa bằng DDD sẽ sử dụng các Bounded Contexts riêng biệt cho từng giai đoạn trong vòng đời. Trong mỗi ngữ cảnh thuộc nhiều Bounded Contexts đó, đều tồn tại một kiểu Book. Các đối tượng Book khác nhau đó sẽ chia sẻ một định danh xuyên suốt tất cả hoặc hầu hết các Contexts, có thể được thiết lập lần đầu tiên ngay từ giai đoạn khái niệm hóa. Tuy nhiên, mô hình của Book trong mỗi Context sẽ hoàn toàn khác biệt so với tất cả các mô hình còn lại. Điều đó hoàn toàn ổn, và trên thực tế đó chính là cách thức mọi việc nên diễn ra. Khi đội ngũ của một Bounded Context nhất định nói về Book, nó mang chính xác ý nghĩa mà họ yêu cầu cho Context của mình. Tổ chức đón nhận nhu cầu tự nhiên về sự khác biệt này. Nói như vậy không có nghĩa là những kết quả tích cực đó có thể đạt được một cách dễ dàng. Dẫu vậy, bằng cách sử dụng các Bounded Contexts tường minh, phần mềm sẽ được bàn giao đều đặn với các cải tiến tăng dần đáp ứng trúng các nhu cầu cụ thể của doanh nghiệp.

> 💡 **Giải thích thêm:** "Churn and burn" là một thành ngữ mô tả trạng thái làm việc cật lực, hao tổn nhiều công sức và tài nguyên nhưng chỉ xoay quanh sự xáo trộn, cọ xát nội bộ mà không tạo ra được kết quả thực tế bền vững nào. Trong phát triển phần mềm, việc cố gắng nhồi nhét mọi yêu cầu của toàn doanh nghiệp vào một mô hình dữ liệu dùng chung duy nhất luôn dẫn đến cảnh các nhóm liên tục tranh cãi, sửa đổi mã nguồn liên miên ("churn and burn") mà không thể phát hành được phiên bản ổn định nào.
> Nguồn tham khảo: (Không có nguồn trích dẫn xác thực — cần tự kiểm chứng thêm)

Đến thời điểm này, chúng ta hãy cùng nhìn nhanh vào giải pháp mà đội ngũ cộng tác của SaaSOvation đã sử dụng để giải quyết thách thức mô hình hóa như được minh họa trong Hình 2.3.

Như đã chỉ ra trước đây, trong một Collaboration Context, các chuyên gia miền không bao giờ mô tả những người sử dụng các tiện ích cộng tác là Users (Người dùng) kèm theo Permissions (Quyền hạn). Thay vào đó, họ trao đổi về những người cộng tác này dựa trên các vai trò mà họ nắm giữ trong Context đó, chẳng hạn như Authors (Tác giả), Owners (Chủ sở hữu), Participants (Người tham gia), và Moderators (Người điều phối). Một vài thông tin liên lạc có thể tồn tại ở đó, nhưng có lẽ không phải là tất cả. Mặt khác, chính trong Identity and Access Context (Ngữ cảnh Định danh và Truy cập), chúng ta mới bàn về Users. Trong Context đó, các đối tượng User có tên người dùng (usernames) và thông tin chi tiết về từng cá nhân cụ thể, bao gồm các phương thức chi tiết để liên lạc với người đó.

Tuy vậy, chúng ta không tạo ra một đối tượng Author từ hư không. Mọi cộng tác viên đều bắt buộc phải được thẩm định điều kiện từ trước. Chúng ta xác nhận sự tồn tại của một User đang đảm nhiệm Role phù hợp bên trong Identity and Access Context. Các thuộc tính của một bộ mô tả xác thực (authentication descriptor) được truyền kèm theo các yêu cầu gửi tới Identity and Access Context. Để tạo một đối tượng cộng tác viên mới, chẳng hạn như một Moderator, chúng ta sử dụng một tập con các thuộc tính của User cùng với một tên Role. Các chi tiết cụ thể về cách thức chúng ta thu nhận trạng thái đối tượng từ một Bounded Context tách biệt không quá quan trọng vào lúc này (mặc dù phần sau sẽ giải thích rất kỹ lưỡng). Điều quan trọng lúc này là hai khái niệm khác biệt này vừa tương đồng lại vừa khác nhau cùng một lúc, và những khác biệt đó được định đoạt bởi chính Bounded Context. Hình 2.6 minh họa User và Role trong Context riêng của chúng được sử dụng để tạo ra một Moderator trong một Context khác.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000042_3039fa20a4801a59138c5be3f1c1e4054c88a2c1ff023610b52fb20869f6d833.png)

Figure 2.6 Đối tượng Moderator trong Context của nó được tạo dựng dựa trên User và Role trong một ngữ cảnh khác.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000043_97c21a7d1de24d73383c96a9be926d4de92641082486243114ccc631941422d0.png)

## Giờ Làm việc với Bảng trắng (Whiteboard Time)

- Hãy xem liệu bạn có thể nhận diện được một số khái niệm có sự khác biệt tinh tế đang tồn tại trong nhiều Bounded Contexts thuộc Domain của bạn hay không.
- Xác định xem liệu các khái niệm đó có được phân tách chuẩn xác hay không, hay các lập trình viên chỉ đơn thuần sao chép mã nguồn sang cả hai nơi.

Nhìn chung, bạn có thể xác định một sự phân tách chuẩn xác nhờ vào việc các đối tượng tương tự nhau sở hữu các thuộc tính và thao tác khác nhau. Trong trường hợp đó, ranh giới đã phân định các khái niệm một cách thỏa đáng. Tuy nhiên, nếu bạn nhìn thấy các đối tượng giống hệt nhau xuất hiện ở nhiều ngữ cảnh, điều đó rất có thể ám chỉ một lỗi mô hình hóa nào đó, trừ khi hai Bounded Contexts đó đang cùng sử dụng một Shared Kernel (Hạt nhân Chia sẻ) (3).

## Không gian cho Những thứ Ngoài Mô hình (Room for More than the Model)

Một Bounded Context không nhất thiết chỉ bao bọc riêng domain model. Đúng là mô hình là cư dân chính của chiếc vỏ chứa khái niệm này. Tuy nhiên, một Bounded Context không hề bị giới hạn ở riêng mô hình. Nó thường phân định ranh giới cho một hệ thống, một ứng dụng hoặc một dịch vụ kinh doanh (business service). [^5] Đôi khi một Bounded Context chứa đựng ít hơn thế nếu, chẳng hạn, một Generic Subdomain có thể được tạo ra mà không cần gì nhiều hơn ngoài một domain model. Hãy xem xét các thành phần của một hệ thống vốn thường là một phần của Bounded Context.

[^5]: Phải thừa nhận rằng ý nghĩa của các thuật ngữ *hệ thống* (system), *ứng dụng* (application) và *dịch vụ kinh doanh* (business service) không phải lúc nào cũng nhận được sự đồng thuận hoàn toàn. Tuy nhiên, theo nghĩa khái quát, tôi muốn ám chỉ những thuật ngữ này là một tập hợp phức tạp gồm các thành phần tương tác với nhau để hiện thực hóa một tập hợp các use cases kinh doanh quan trọng.

Khi mô hình dẫn dắt việc tạo ra một lược đồ cơ sở dữ liệu lưu trữ bền vững (persistence database schema), lược đồ cơ sở dữ liệu đó sẽ nằm bên trong ranh giới. Điều này diễn ra bởi vì lược đồ được thiết kế, phát triển và bảo trì bởi chính đội ngũ mô hình hóa. Điều đó có nghĩa là tên bảng và tên cột cơ sở dữ liệu, chẳng hạn, sẽ phản ánh trực tiếp các tên gọi được sử dụng trong mô hình, thay vì các tên gọi bị phiên dịch sang một phong cách khác. Ví dụ, giả sử mô hình của chúng ta có một lớp tên là BacklogItem và lớp đó có các thuộc tính Value Object tên là backlogItemId và businessPriority:


```

public class BacklogItem extends Entity  { ... private BacklogItemId backlogItemId; private BusinessPriority businessPriority; ... }

```

Chúng ta sẽ kỳ vọng nhìn thấy những thuộc tính đó được ánh xạ vào cơ sở dữ liệu theo cách thức tương tự:


```

CREATE TABLE `tbl_backlog_item` ( ... `backlog_item_id_id` varchar(36) NOT NULL, `business_priority_ratings_benefit` int NOT NULL, `business_priority_ratings_cost` int NOT NULL, `business_priority_ratings_penalty` int NOT NULL, `business_priority_ratings_risk` int NOT NULL, ... ) ENGINE=InnoDB;

```

Mặt khác, nếu một lược đồ cơ sở dữ liệu đã tồn tại từ trước hoặc nếu một đội ngũ chuyên gia mô hình hóa dữ liệu riêng biệt áp đặt các thiết kế mâu thuẫn lên lược đồ cơ sở dữ liệu, thì lược đồ đó không nằm bên trong Bounded Context mà domain model đang chiếm giữ.

Khi có các khung nhìn Giao diện Người dùng (UI - User Interface) (14) thực hiện việc kết xuất (render) mô hình và dẫn dắt việc thực thi hành vi của nó, các khung nhìn này cũng nằm bên trong Bounded Context. Tuy nhiên, điều này không có nghĩa là chúng ta mô hình hóa Domain ngay trên giao diện người dùng, gây ra tình trạng thiếu máu cho domain model. Chúng ta muốn khước từ Phản mẫu Giao diện Thông minh (Smart UI Anti-Pattern) [Evans] cùng bất kỳ sự cám dỗ nào trong việc lôi kéo các khái niệm miền vốn thuộc về mô hình sang các khu vực khác của hệ thống.

Người dùng của hệ thống/ứng dụng không phải lúc nào cũng chỉ giới hạn ở con người mà có thể bao gồm các hệ thống máy tính khác. Các thành phần như Web services có thể tồn tại. Chúng ta có thể sử dụng các tài nguyên RESTful để cung cấp sự tương tác với mô hình dưới dạng một Open Host Service (Dịch vụ Máy chủ Mở) (3, 13). Hoặc có thể chúng ta triển khai các điểm cuối dịch vụ SOAP (Simple Object Access Protocol - Giao thức Truy cập Đối tượng Đơn giản) hay dịch vụ truyền thông điệp (messaging) thay thế. Trong tất cả các trường hợp đó, các thành phần hướng dịch vụ này đều nằm bên trong ranh giới.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000044_2ab0998e2aca6354bb60f7a8af17dfd4eac8c424e7b0907d491f7b148af4d510.png)

Cả các thành phần giao diện người dùng lẫn các điểm cuối hướng dịch vụ đều ủy quyền xử lý cho các Application Services (Dịch vụ Ứng dụng) (14). Đây là các loại dịch vụ khác biệt, nhìn chung cung cấp khả năng bảo mật và quản lý giao dịch, đồng thời đóng vai trò như một Facade (Mẫu hình Mặt tiền) [Gamma et al.] che chắn cho mô hình. Chúng là những bộ quản lý tác vụ, chuyển đổi các yêu cầu luồng use case thành việc thực thi logic miền. Các Application Services cũng nằm bên trong ranh giới.

## Tìm hiểu thêm về các Mối quan tâm Kiến trúc và Ứng dụng (More on Architectural and Application Concerns)

Nếu bạn muốn tìm hiểu xem DDD hòa hợp như thế nào với các phong cách kiến trúc đa dạng, hãy xem chương Kiến trúc (Architecture) (4). Ngoài ra, Application Services được mổ xẻ đặc biệt trong chương Ứng dụng (Application) (14). Có rất nhiều sơ đồ và đoạn mã hữu ích trong cả hai chương này.

Bounded Context trước hết đóng gói Ubiquitous Language và domain model của nó, nhưng nó bao hàm cả những gì tồn tại nhằm cung cấp sự tương tác với và hỗ trợ cho domain model. Hãy chú ý giữ cho các khía cạnh của từng mối bận tâm Kiến trúc nằm đúng vị trí của chúng.

## Giờ Làm việc với Bảng trắng (Whiteboard Time)

- Hãy nhìn vào từng Bounded Context mà bạn đã xác định trong sơ đồ bảng trắng của mình. Khi nghĩ về những ngữ cảnh đó, bạn có hình dung các thành phần ngoài domain model cũng nằm bên trong ranh giới không?
- Nếu có một giao diện người dùng và một tập hợp các Application Services, hãy đảm bảo chúng nằm bên trong ranh giới. (Bạn có sự linh hoạt trong cách thức biểu diễn những thành phần này. Hãy xem Hình 2.8, 2.9 và 2.10 để có một số ý tưởng biểu diễn các thành phần khác nhau.)
- Nếu lược đồ cơ sở dữ liệu hoặc kho lưu trữ bền vững khác được phát triển cho mô hình của bạn, hãy đảm bảo nó cũng nằm bên trong ranh giới. (Hình 2.8, 2.9 và 2.10 cung cấp một cách để biểu diễn lược đồ cơ sở dữ liệu.)

## Quy mô của Bounded Contexts (Size of Bounded Contexts)

Một Bounded Context nên chứa bao nhiêu Modules (9), Aggregates (10), Events (8) và Services (7) — những khối xây dựng chính của một domain model được tạo ra bằng DDD? Câu hỏi đó hơi giống câu: "Một sợi dây dài bao nhiêu?" Một Bounded Context nên có độ lớn vừa đủ như nó cần phải có để biểu đạt trọn vẹn Ubiquitous Language hoàn chỉnh của nó.

> 💡 **Giải thích thêm:** "How long is a piece of string?" (Một sợi dây dài bao nhiêu?) là một thành ngữ tiếng Anh chỉ câu hỏi không thể có câu trả lời duy nhất hay con số cố định, bởi vì câu trả lời hoàn toàn phụ thuộc vào từng trường hợp cụ thể. Ở đây, tác giả muốn nhấn mạnh rằng quy mô của một Bounded Context không thể đo đếm bằng số lượng lớp hay số dòng mã cố định, mà phụ thuộc hoàn toàn vào phạm vi của Ubiquitous Language cần được biểu đạt.
> Nguồn tham khảo: (Không có nguồn trích dẫn xác thực — cần tự kiểm chứng thêm)

Những khái niệm ngoại lai không thực sự là một phần của Core Domain cần phải được loại bỏ ra ngoài. Nếu một khái niệm không nằm trong Ubiquitous Language của bạn, ngay từ đầu nó không nên được đưa vào mô hình. Dẫu vậy, nếu có một hoặc nhiều khái niệm ngoại lai len lỏi vào, hãy loại bỏ chúng. Chúng có thể thuộc về một Supporting Subdomain hoặc Generic Subdomain riêng biệt, hoặc hoàn toàn không thuộc về bất kỳ mô hình nào cả.

Hãy cẩn thận để không vô tình loại bỏ nhầm những khái niệm thực sự thuộc về Core Domain. Mô hình của bạn bắt buộc phải thể hiện đầy đủ sự phong phú của Ubiquitous Language trong ngữ cảnh, không được bỏ sót bất kỳ điều gì thiết yếu. Rõ ràng, cần phải có sự phán đoán sáng suốt. Các công cụ như Context Maps (3) có thể hỗ trợ định hình khả năng phán đoán sáng suốt của đội ngũ bạn.

Trong bộ phim *Amadeus*, [^6] có một cảnh quay nơi Hoàng đế Áo Joseph II nhận xét với Mozart rằng tác phẩm âm nhạc mà Mozart vừa biểu diễn là một tác phẩm chất lượng, nhưng nó chứa đựng "đơn giản là quá nhiều nốt nhạc". Mozart đã đáp lại hoàng đế một cách sắc sảo: "Có đúng bằng ấy nốt nhạc mà tôi yêu cầu, không thừa cũng chẳng thiếu." Câu trả lời này minh họa hoàn hảo cho tư duy thiết yếu cần mang theo khi vạch ra các ranh giới ngữ cảnh bao quanh các mô hình của chúng ta. Có một số lượng khái niệm miền rất thích hợp để mô hình hóa trong một Bounded Context nhất định, không thừa cũng chẳng thiếu.

[^6]: Orion Pictures, Warner Brothers, 1984.

Tất nhiên, điều này hiếm khi dễ dàng đối với mỗi chúng ta như khi Mozart sáng tác một bản giao hưởng với sự thanh thoát như viết một lá thư cho bạn bè. Tại bất kỳ thời điểm nào, chúng ta có thể đã bỏ lỡ cơ hội tinh chỉnh domain model ở một mức độ nào đó. Trong mỗi vòng lặp (iteration), chúng ta thách thức các giả định của mình về mô hình, điều này buộc chúng ta phải thêm hoặc bớt một khái niệm, hoặc thay đổi cách thức các khái niệm hành xử và cộng tác với nhau. Nhưng mấu chốt là chúng ta đối mặt với thách thức đó hết lần này đến lần khác, và bằng cách sử dụng các nguyên lý DDD, chúng ta suy xét nghiêm túc về những gì thuộc về mô hình và những gì không. Chúng ta sử dụng Bounded Context và các công cụ như Context Maps để giúp phân tích xem điều gì thực sự là một phần của một Core Domain. Chúng ta không viện đến việc áp dụng các quy tắc chia tách tùy tiện dựa trên các nguyên lý phi DDD.

## Âm thanh Tuyệt mỹ của các Mô hình Miền (The Beautiful Sound of Domain Models)

Nếu các mô hình của chúng ta là âm nhạc, chúng sẽ mang âm thanh không thể nhầm lẫn của sự trọn vẹn, thuần khiết, sức mạnh, và thậm chí có thể là sự thanh lịch và vẻ đẹp tuyệt mỹ.

Nếu chúng ta gò ép một Bounded Context quá khắt khe, những lỗ hổng to lớn sẽ xuất hiện do thiếu vắng các khái niệm ngữ cảnh mang tính sống còn. Và nếu chúng ta tiếp tục chất đống các khái niệm lên mô hình vốn không hề diễn đạt phần cốt lõi của bài toán kinh doanh đang được giải quyết, chúng ta sẽ làm vẩn đục dòng nước đến mức không thể quan sát và thấu hiểu được những gì là thiết yếu. Mục tiêu của chúng ta là gì? Nếu các mô hình của chúng ta là âm nhạc, chúng sẽ mang âm thanh không thể nhầm lẫn của sự trọn vẹn, thuần khiết, sức mạnh, và thậm chí có thể là sự thanh lịch và vẻ đẹp tuyệt mỹ. Số lượng nốt nhạc — tức các Modules, Aggregates, Events và Services bên trong — sẽ không nhiều hơn cũng chẳng ít hơn những gì một thiết kế chuẩn xác đòi hỏi. Những ai "lắng nghe" mô hình sẽ không bao giờ phải thắc mắc xem "âm thanh" kỳ lạ kia là gì ở giữa một bản giao hưởng vốn dĩ đang rất hài hòa. Họ cũng sẽ không bị phân tâm bởi những khoảnh khắc im lặng hoàn toàn gây ra bởi một hoặc hai trang nốt nhạc bị mất tích.

Điều gì có thể dẫn dắt chúng ta tạo ra một Bounded Context có kích thước sai lệch? Chúng ta có thể đã sai lầm khi để cho các ảnh hưởng kiến trúc, thay vì Ubiquitous Language, dẫn dắt mình. Có lẽ cách thức một nền tảng, một framework hay một hạ tầng nào đó thường được sử dụng để đóng gói và triển khai các thành phần đã gây ảnh hưởng không đáng có lên cách chúng ta tư duy về Bounded Contexts, đối xử với chúng như những ranh giới kỹ thuật thay vì ranh giới ngôn ngữ.

Một cạm bẫy khác là chia nhỏ các Bounded Contexts nhằm mục đích phân chia công việc cho các nguồn lực lập trình viên sẵn có. Các trưởng nhóm kỹ thuật (technical leads) và quản lý dự án có thể nghĩ rằng các lập trình viên sẽ dễ quản lý các tác vụ nhỏ hơn. Mặc dù điều đó có thể đúng, nhưng việc áp đặt ranh giới chỉ vì mục đích phân bổ tác vụ là hành vi đi ngược lại các động lực ngôn ngữ của việc mô hình hóa ngữ cảnh. Trên thực tế, hoàn toàn không cần thiết phải áp đặt các ranh giới giả tạo để quản lý các nguồn lực kỹ thuật.

Câu hỏi quan trọng là: Ngôn ngữ của các chuyên gia miền chỉ ra điều gì về các ranh giới ngữ cảnh thực sự?

Khi một Context giả tạo được dựng lên để phục vụ cho một thành phần kiến trúc hoặc nguồn lực lập trình viên, Ngôn ngữ sẽ bị phân mảnh và thiếu đi tính biểu đạt. Do đó, hãy tập trung vào Core Domain với các khái niệm tự nhiên ăn khớp với nhau thành một Bounded Context duy nhất, dựa theo Ngôn ngữ được các chuyên gia miền sử dụng. Sau khi làm như vậy, bạn có thể xác định các thành phần vốn tự nhiên thuộc về một mô hình gắn kết, đơn lẻ. Hãy giữ tất cả các thành phần như vậy bên trong Bounded Context.

Đôi khi vấn đề tạo ra các Bounded Contexts siêu nhỏ (miniature) có thể tránh được nhờ việc áp dụng cẩn trọng các Modules. Thông qua việc phân tích một tập hợp các dịch vụ đang nằm rải rác trên nhiều "Bounded Contexts", bạn sẽ nhận thấy rằng việc sử dụng Modules một cách khôn ngoan có thể thu gọn tổng số Bounded Contexts thực tế xuống chỉ còn đúng một. Modules cũng có thể được sử dụng như một phương tiện để phân chia trách nhiệm của các lập trình viên, từ đó quản lý việc phân bổ công việc bằng một phương pháp tiếp cận chiến thuật phù hợp hơn.

## Giờ Làm việc với Bảng trắng (Whiteboard Time)

- Hãy vẽ một Bounded Context cho mô hình hiện tại của bạn dưới dạng một hình elip lớn, méo mó bất định.
- Ngay cả khi bạn chưa có một mô hình tường minh, hãy cứ suy nghĩ về Ngôn ngữ bên trong đó.
- Bên trong hình elip, hãy viết tên của các khái niệm chính mà bạn chắc chắn rằng mã nguồn của mình đang triển khai. Hãy xem liệu bạn có thể phát hiện ra những khái niệm đáng lẽ phải có mặt nhưng lại bị thiếu, và những khái niệm đang xuất hiện ở đó nhưng không nên có mặt hay không. Bạn nên làm gì đối với từng vấn đề đó?

## Hãy Cẩn trọng Thực hành DDD Dựa trên các Yếu tố Dẫn dắt Ngôn ngữ (Be Careful to Practice DDD Using Linguistic Drivers)

Điểm mấu chốt: Nếu bạn không tuân theo các yếu tố dẫn dắt Ngôn ngữ, bạn đang không làm việc cùng và không lắng nghe các chuyên gia miền để tạo ra Bounded Context. Hãy suy nghĩ cẩn trọng về quy mô của các Bounded Contexts của bạn. Đừng vội vàng chia nhỏ chúng thành các mảnh vụn.

## Điều chỉnh Khớp với các Thành phần Kỹ thuật (Aligning with Technical Components)

Cũng không có hại gì khi tư duy về một Bounded Context dưới góc độ của các thành phần kỹ thuật chứa đựng nó. Chỉ cần ghi nhớ rằng các thành phần kỹ thuật không định nghĩa nên Context. Hãy cùng xem xét một số cách thức phổ biến mà chúng được cấu thành và triển khai.

Khi sử dụng một IDE (Integrated Development Environment - Môi trường Phát triển Tích hợp) như Eclipse hoặc IntelliJ IDEA, một Bounded Context thường được đặt trong một project (dự án) duy nhất. Khi sử dụng Visual Studio và .NET, bạn có thể thích chia giao diện người dùng, Application Services và domain model thành các project riêng biệt trong cùng một solution (giải pháp), hoặc bạn có thể quyết định một cách phân chia khác. Cây thư mục mã nguồn của project có thể chỉ giới hạn ở riêng domain model, hoặc nó có thể chứa các khu vực bao quanh thuộc Layers (Các Tầng kiến trúc) (4) hoặc Hexagonal (Kiến trúc Lục giác) (4). Có rất nhiều sự linh hoạt tại đây. Khi sử dụng Java, package ở cấp cao nhất thường định nghĩa tên Module cấp cao nhất cho Bounded Context. Sử dụng một trong những ví dụ trước đó, điều đó có thể được thực hiện tương tự như sau:


```

com.mycompany.optimalpurchasing

```

Cây thư mục mã nguồn của Bounded Context này sẽ được chia nhỏ tiếp theo các trách nhiệm Kiến trúc. Dưới đây là một góc nhìn về các tên package cấp hai khả dĩ của project:


```

com.mycompany.optimalpurchasing.presentation com.mycompany.optimalpurchasing.application com.mycompany.optimalpurchasing.domain.model com.mycompany.optimalpurchasing.infrastructure

```

Ngay cả với những sự phân chia module này, chỉ nên có một đội ngũ duy nhất làm việc trong một Bounded Context duy nhất.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000045_4415a2bfa95ae5c81b4147b2769d4e14d38ba699e28a1d4b5b6e95ce650e801b.png)

## Một Đội ngũ Duy nhất cho Một Bounded Context Duy nhất (A Single Team for a Single Bounded Context)

Việc chỉ định một đội ngũ duy nhất làm việc trên một Bounded Context duy nhất không phải là một nỗ lực nhằm hạn chế tính linh hoạt trong tổ chức nhóm. Không phải là các nhóm không thể được sắp xếp lại khi cần, hay các thành viên riêng lẻ của một nhóm không thể tham gia vào một hoặc nhiều dự án khác. Một công ty nên sử dụng nhân sự theo cách phù hợp nhất với nhu cầu của mình. Điều này chỉ đơn giản khẳng định rằng tốt nhất là một đội ngũ gắn kết, được xác định rõ ràng gồm các chuyên gia miền và các lập trình viên nên tập trung vào một Ubiquitous Language duy nhất được mô hình hóa trong một Bounded Context tường minh. Nếu bạn chỉ định từ hai nhóm riêng biệt trở lên cho một Bounded Context, mỗi nhóm sẽ góp phần tạo ra một Ubiquitous Language bị phân kỳ và thiếu chuẩn xác.

Ngoài ra cũng có khả năng hai nhóm sẽ hợp tác trong việc thiết kế một Shared Kernel (Hạt nhân Chia sẻ), vốn thực tế không phải là một Bounded Context điển hình. Mẫu hình Context Mapping này hình thành một mối quan hệ mật thiết giữa hai nhóm, đòi hỏi sự tham vấn liên tục khi các thay đổi mô hình được coi là cần thiết. Phương pháp mô hình hóa này ít phổ biến hơn và nhìn chung nên tránh nếu có thể.

Khi sử dụng Java, về mặt kỹ thuật chúng ta có thể chứa một Bounded Context trong một hoặc nhiều file JAR, bao gồm cả các file WAR hoặc EAR. Mong muốn module hóa có thể tạo ra ảnh hưởng ở đây. Các phần có độ phụ thuộc lỏng lẻo (loosely coupled) của domain model có thể được đặt trong các file JAR riêng biệt, cho phép chúng được triển khai độc lập theo từng phiên bản. Điều này sẽ đặc biệt hữu ích đối với các mô hình lớn. Việc tạo ra nhiều file JAR từ một mô hình đơn lẻ sẽ mang lại lợi thế quản lý phiên bản của các phần tử bên trong nó bằng cách sử dụng các OSGi bundles hoặc các module Java 8 Jigsaw. Do đó, các module cấp cao khác nhau, phiên bản của chúng và các phụ thuộc của chúng có thể được quản lý dưới dạng các bundles/modules. Có ít nhất bốn bundles/modules như vậy được đại diện bởi các Modules cấp hai dựa trên DDD ở trên, và có thể còn nhiều hơn thế.

Đối với một Bounded Context chạy native trên Windows, chẳng hạn như cho nền tảng .NET, việc triển khai sẽ được thực hiện bằng cách sử dụng các assembly riêng biệt trong các file DLL. Hãy coi một file DLL có những động lực triển khai tương tự như file JAR được mô tả ở trên. Mô hình có thể được phân vùng để triển khai theo những cách tương tự. Toàn bộ việc module hóa trong CLR (Common Language Runtime - Môi trường Thực thi Ngôn ngữ Chung) đều được quản lý thông qua các assemblies. Phiên bản cụ thể của một assembly và các phiên bản của các assembly phụ thuộc đều được ghi lại trong manifest của assembly đó. Xem [MSDN Assemblies].

## Các Ngữ cảnh Mẫu (Sample Contexts)

Bởi vì các mẫu ví dụ đại diện cho một môi trường phát triển mới hoàn toàn (greenfield), ba Bounded Contexts được chọn lựa cuối cùng đã ăn khớp theo cách đáng mong đợi nhất, theo tỷ lệ một-đối-một, với các Subdomains tương ứng của chúng. Nhóm đã không thành công trong việc căn chỉnh chúng theo tỷ lệ một-đối-một ngay từ đầu, điều này mang lại một bài học mang tính sống còn. Kết quả cuối cùng được thể hiện trong Hình 2.7.

Figure 2.7 Góc nhìn đánh giá của các Bounded Contexts mẫu trong các Subdomains được căn chỉnh hoàn toàn

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000046_851b2e82f94cbd978a0ae2959b26baa373ad417b04742a4e783d9182b1c70b65.png)

Nội dung sau đây chứng minh cách thức ba mô hình này tạo nên một giải pháp doanh nghiệp hiện đại, thực tế. Luôn luôn có nhiều Bounded Contexts trong bất kỳ dự án nào ngoài đời thực. Sự tích hợp giữa chúng là một kịch bản quan trọng trong doanh nghiệp ngày nay. Bên cạnh Bounded Context và Subdomains, chúng ta cũng bắt buộc phải nắm vững Context Mapping cùng với Tích hợp (Integration) (13).

Hãy cùng xem xét ba Bounded Contexts được cung cấp làm các ví dụ triển khai DDD mẫu. [^7] Chúng bao gồm Collaboration Context (Ngữ cảnh Cộng tác), Identity and Access Context (Ngữ cảnh Định danh và Truy cập), và Agile Project Management Context (Ngữ cảnh Quản lý Dự án Agile).

[^7]: Lưu ý rằng chương Context Maps cung cấp thêm chi tiết về ba Bounded Contexts mẫu thực tế này, cách chúng liên hệ với nhau ra sao và chúng được tích hợp như thế nào. Dẫu vậy, độ sâu vẫn được tập trung nhiều hơn vào Core Domain.

## Ngữ cảnh Cộng tác (Collaboration Context)

Các công cụ cộng tác kinh doanh là một trong những khu vực quan trọng nhất để tạo ra và thúc đẩy một môi trường làm việc cộng hưởng trong nền kinh tế có nhịp độ phát triển nhanh chóng. Bất cứ điều gì có thể giúp gia tăng năng suất, chuyển giao tri thức, thúc đẩy chia sẻ ý tưởng và quản lý liên kết quy trình sáng tạo để các kết quả không bị thất lạc đều là một cú hích lớn cho phương trình thành công của doanh nghiệp. Cho dù các công cụ phần mềm cung cấp các tính năng cho các cộng đồng rộng lớn hay cho các đối tượng thu hẹp nhắm vào các hoạt động và dự án hàng ngày, các tập đoàn đều đang đổ xô tìm đến các công cụ trực tuyến tốt nhất trong từng phân khúc, và SaaSOvation muốn có một phần của miếng bánh thị trường đó.

Đội ngũ nòng cốt được giao nhiệm vụ thiết kế và triển khai Collaboration Context đã nhận được chỉ thị phát hành phiên bản đầu tiên bắt buộc phải hỗ trợ bộ công cụ tối thiểu sau: diễn đàn (forums), lịch chia sẻ (shared calendars), blog, nhắn tin tức thời (instant messaging), wiki, bảng tin (message boards), quản lý tài liệu (document management), thông báo và cảnh báo (announcements and alerts), theo dõi hoạt động (activity tracking), và các nguồn cấp RSS. Trong khi hỗ trợ một loạt các tính năng phong phú, từng công cụ cộng tác riêng lẻ trong bộ phần mềm cũng có thể hỗ trợ các môi trường nhóm có mục tiêu hẹp, chuyên biệt, nhưng chúng vẫn nằm trong cùng một Bounded Context vì tất cả đều là một phần của sự cộng tác. Đáng tiếc là cuốn sách này không thể cung cấp toàn bộ bộ công cụ cộng tác đó. Tuy nhiên, chúng ta có khám phá các phần của domain model dành cho các công cụ được đại diện trong Hình 2.8, cụ thể là Diễn đàn (Forums) và Lịch Chia sẻ (Shared Calendars).

Bây giờ, hãy đến với trải nghiệm thực tế của đội ngũ . . .

Figure 2.8 Collaboration Context. Ubiquitous Language của nó quyết định những gì thuộc về bên trong ranh giới. Để dễ đọc, một số phần tử mô hình không được hiển thị. Điều tương tự cũng áp dụng cho các thành phần giao diện người dùng (UI) và Application Service.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000047_7cc261b86e96121a179853d353d3b0ede2c35817f4d06cd1f3d1101f0d7e3d45.png)

DDD chiến thuật đã được sử dụng ngay từ khi bắt đầu phát triển sản phẩm, nhưng nhóm vẫn đang trong quá trình học hỏi một số điểm tinh tế hơn của DDD. Trên thực tế, những gì họ đang sử dụng thực chất chỉ tương đương với DDD-Lite, vận dụng các mẫu hình chiến thuật chủ yếu vì mục đích lợi ích kỹ thuật. Đúng vậy, họ đang cố gắng nắm bắt Ubiquitous Language của sự cộng tác, nhưng họ không hiểu rằng mô hình có những giới hạn rõ ràng không thể bị kéo dãn quá mức. Kết quả là, họ đã mắc sai lầm khi nhồi nhét bảo mật và phân quyền vào bên trong

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000048_999e1ff18d315cb84e79d6926e98241cdae48a2812b61d6c0cacce81e06c9acc.png)

mô hình cộng tác. Phải đến khi tiến sâu vào dự án, cả nhóm mới nhận ra rằng việc thiết kế bảo mật và phân quyền như một phần trong mô hình của mình là điều không hề đáng mong muốn như họ từng nghĩ.

Giai đoạn đầu họ không quá bận tâm hoặc chưa nhận thức đầy đủ về mối nguy hiểm của việc xây dựng một ốc đảo ứng dụng biệt lập (application silo). Thế nhưng, nếu không sử dụng một nhà cung cấp bảo mật tập trung, đó chính xác là những gì sẽ xảy ra. Điều đó cấu thành việc trộn lẫn hai mô hình vào làm một. Chẳng bao lâu sau, họ hiểu ra rằng sự vướng víu hỗn độn bắt nguồn từ việc hòa trộn các mối bận tâm bảo mật vào trong Core Domain đã phản tác dụng. Ngay giữa logic nghiệp vụ cốt lõi, trong các phương thức hành vi, các lập trình viên lại đi kiểm tra quyền hạn của client để thực hiện yêu cầu:


```

public class Forum extends Entity { ... public Discussion startDiscussion( String aUsername, String aSubject) { if (this.isClosed()) { throw new IllegalStateException("Forum is closed."); } User user = userRepository.userFor(this.tenantId(), aUsername); if (!user.hasPermissionTo(Permission.Forum.StartDiscussion)) { throw new IllegalStateException( "User may not start forum discussion."); } String authorUser = user.username(); String authorName = user.person().name().asFormattedName(); String authorEmailAddress = user.person().emailAddress(); Discussion discussion = new Discussion( this.tenant(), this.forumId(), DomainRegistry.discussionRepository().nextIdentity(), authorUser, authorName, authorEmailAddress, aSubject); return discussion; } ... }

```

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000049_3326297795cb56df95a96aa408e40719072d70e2fe16d8c791168aca3147a7c2.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000050_89026c27069496ac08c39d27bd46b8a230a9157de6b6c876ec9cdcb684dfc441.png)

## Có Phải Tôi Vừa Thấy một Vụ Tai nạn Dồn toa? (Did I Just See a Train Wreck?)

Một số lập trình viên coi việc xâu chuỗi nhiều biểu thức liên tiếp, chẳng hạn như `user.person().name().asFormattedName()`, là một "vụ tai nạn tàu hỏa dồn toa" (train wreck). Những người khác lại coi đó là khả năng biểu đạt mạch lạc trong mã nguồn. Tôi không bàn luận về cả hai góc nhìn đó tại đây. Thay vào đó, tôi đang tập trung vào mô hình bị hỗn tạp. Vấn đề "tai nạn dồn toa" là một chủ đề hoàn toàn khác.

> 💡 **Giải thích thêm:** Trong lập trình hướng đối tượng, "Train wreck" (tai nạn dồn toa / chuỗi phương thức nối đuôi) là thuật ngữ chỉ các dòng mã gọi hàm liên hoàn dạng `a.getB().getC().getD()`, nhìn tựa như các toa tàu đâm dồn vào nhau. Lối viết này vi phạm nghiêm trọng Luật Demeter (Law of Demeter - nguyên lý chỉ nói chuyện với bạn bè thân cận nhất) và nguyên lý "Tell, Don't Ask", làm lộ cấu trúc nội bộ của đối tượng và khiến mã nguồn trở nên giòn gãy, dễ đổ vỡ khi cấu trúc dữ liệu thay đổi.
> Nguồn tham khảo: (Không có nguồn trích dẫn xác thực — cần tự kiểm chứng thêm)

Đây thực sự là một thiết kế rất tồi tệ. Các lập trình viên lẽ ra không được phép tham chiếu tới User tại đây, chứ đừng nói đến việc truy vấn một Repository (12) để lấy ra một User. Ngay cả Permission lẽ ra cũng phải nằm ngoài tầm với. Điều này xảy ra được là do chúng đã bị thiết kế sai lầm khi đưa vào làm một phần của mô hình cộng tác. Hơn thế nữa, sự bóp méo này đã khiến họ bỏ qua một khái niệm đáng lẽ ra họ phải mô hình hóa: Author (Tác giả). Thay vì gom ba thuộc tính liên quan chặt chẽ vào trong một Value Object tường minh, các lập trình viên dường như lại thỏa mãn với việc xử lý các phần tử dữ liệu này một cách rời rạc. Vấn đề bảo mật đã choán hết tâm trí của họ thay vì sự cộng tác.

Đây không phải là một trường hợp cá biệt. Mọi đối tượng cộng tác đều gặp phải những vấn đề tương tự. Khi nguy cơ tạo ra một Big Ball of Mud đã cận kề trước mắt, cả nhóm quyết định mã nguồn bắt buộc phải thay đổi. Hơn nữa, nhóm cũng muốn chuyển từ phương pháp tiếp cận bảo mật dựa trên quyền hạn (permissions) sang sử dụng quản lý truy cập dựa trên vai trò (role-based access management). Họ sẽ phải làm gì?

Là những người sử dụng các phương pháp luận phát triển agile và trong tương lai sẽ là những người xây dựng các công cụ quản lý dự án agile, họ không hề e ngại việc áp dụng các nỗ lực tái cấu trúc (refactoring) đúng lúc (just in time). Vì vậy, họ sẽ tái cấu trúc theo từng vòng lặp. Dẫu vậy, câu hỏi vẫn còn đó: Những mẫu hình DDD nào là tối ưu nhất để đưa họ thoát khỏi tình cảnh tồi tệ này — một vũng lầy sâu hoắm của mã nguồn đặt sai vị trí?

Khi một vài thành viên trong nhóm dành thêm nhiều giờ nghiền ngẫm các mẫu hình khối xây dựng chiến thuật của [Evans], họ nhận ra rằng những mẫu hình này không phải là câu trả lời. Họ đã làm theo hướng dẫn trong các mẫu hình đó để tạo ra các Aggregates bằng cách kết hợp các Entities và Value Objects theo phương diện kỹ thuật. Họ cũng đã sử dụng Repositories và Domain Services (7). Tuy nhiên, họ vẫn đang bỏ sót một điều gì đó quan trọng, và rất có thể điều này báo hiệu sự cần thiết phải chú ý kỹ hơn đến nửa sau của cuốn sách [Evans].

Cuối cùng khi làm như vậy, họ đã ghi nhận được một số kỹ thuật mang lại sức mạnh to lớn. Khi họ nghiền ngẫm 'Phần III: Tái cấu trúc Hướng tới Thấu hiểu Sâu sắc hơn' (Part III: Refactoring toward Deeper Insight) [Evans], điều hiển nhiên là DDD mang lại nhiều điều hơn họ từng nghĩ rất nhiều. Với các kỹ thuật thu lượm được từ phần đó của [Evans], giờ đây họ đã biết cách làm thế nào để có thể cải thiện mô hình hiện tại của mình bằng cách chú ý kỹ hơn tới Ubiquitous Language. Bằng cách dành nhiều thời gian chất lượng hơn với các chuyên gia miền của mình, họ có thể tạo ra một mô hình bám sát hơn mô hình tư duy của các chuyên gia. Nhưng điều đó vẫn chưa giải quyết được vũng lầy bảo mật vốn đang làm méo mó tầm nhìn của họ về một domain model cộng tác thuần khiết.

Đi sâu hơn vào cuốn sách, có 'Phần IV: Thiết kế Chiến lược' (Part IV: Strategic Design) [Evans]. Một trong các thành viên trong nhóm đã tìm thấy những chỉ dẫn mang tính sống còn mà cuối cùng sẽ dẫn dắt họ tới việc hiện thực hóa một Core Domain. Một trong những công cụ mới đầu tiên được đưa vào sử dụng là Context Maps, dẫn đến sự thấu hiểu rõ ràng hơn về tình hình dự án hiện tại của họ. Mặc dù là một bài tập đơn giản, việc vẽ ra Context Map đầu tiên và định hình các cuộc thảo luận xoay quanh tình cảnh khó khăn của họ là một bước tiến lớn. Nó đã dẫn đến những phân tích hiệu quả hướng tới một giải pháp tháo gỡ, và cuối cùng đã khai thông thế bế tắc cho cả nhóm.

Giờ đây họ có một vài lựa chọn để thực hiện những tinh chỉnh tạm thời, cho phép họ ổn định mô hình đang ngày càng trở nên giòn gãy (brittle) của mình:

1. Họ có thể tái cấu trúc mô hình thành Responsibility Layers (Các Tầng Trách nhiệm) [Evans], phân chia các tính năng bảo mật và phân quyền bằng cách đẩy chúng xuống một tầng logic thấp hơn của mô hình hiện tại. Nhưng đó dường như không phải là phương pháp tiếp cận tối ưu nhất. Việc sử dụng Responsibility Layers nhằm mục đích giải quyết các mô hình quy mô lớn, hoặc để chuẩn bị cho những mô hình cuối cùng sẽ phát triển lên quy mô lớn. Mỗi tầng được thiết kế để vẫn nằm lại trong mô hình vì nó là một phần của Core Domain, mặc dù các tầng nên được phân chia cẩn thận. Mặt khác, những gì nhóm đang phải đối mặt lại là những khái niệm bị chiếm dụng sai chỗ — những khái niệm hoàn toàn không thuộc về Core Domain.
2. Ngoài ra, họ có thể hướng tới việc xây dựng một Segregated Core (Lõi Tách biệt) [Evans]. Điều này có thể đạt được thông qua một cuộc rà soát toàn diện mọi mối quan tâm về bảo mật và phân quyền trong Collaboration Context, tiếp nối bằng việc tái cấu trúc các thành phần định danh và truy cập vào các package hoàn toàn tách biệt trong cùng một mô hình. Cách làm này sẽ chưa mang lại kết quả tối hậu là tạo ra một Bounded Context hoàn toàn độc lập, nhưng nó sẽ đưa nhóm tiến gần hơn tới đích đến đó. Đây dường như chính xác là những gì đang cần, bởi bản thân mẫu hình này đã nêu rõ: 'Thời điểm để bóc tách một Segregated Core là khi bạn có một Bounded Context lớn mang tính sống còn đối với hệ thống, nhưng nơi mà phần cốt lõi thiết yếu của mô hình đang bị che mờ bởi một lượng lớn các năng lực hỗ trợ.' Năng lực hỗ trợ ở đây chắc chắn chính là bảo mật và phân quyền. Đội ngũ cuối cùng đã nhận ra rằng một Identity and Access Context riêng biệt sẽ xuất hiện từ những nỗ lực này và đóng vai trò như một Generic Subdomain phục vụ cho Collaboration Context của họ.

Sáng kiến tạo ra một Segregated Core sẽ không hề đơn giản. Nó có thể đòi hỏi vài tuần làm việc ngoài kế hoạch. Nhưng nếu họ không có hành động khắc phục và tái cấu trúc sớm, họ sẽ phải trả giá cho sự thiếu hụt hành động khắc phục đó bằng hàng đống lỗi (bugs), đi kèm với một cơ sở mã (code base) mỏng manh không thể đáp ứng tốt với sự thay đổi. Lãnh đạo doanh nghiệp đã góp phần củng cố tính đúng đắn của định hướng này khi họ nhận định rằng việc tách biệt thành công thành một dịch vụ kinh doanh mới vào một ngày nào đó hoàn toàn có thể mở đường cho một sản phẩm SaaS hoàn toàn mới.

Quan trọng nhất là, giờ đây cả nhóm đã hiểu được giá trị của Bounded Contexts và của việc phải chiến đấu kiên cường để duy trì một Core Domain có tính gắn kết cao. Sử dụng các mẫu hình bổ sung của thiết kế chiến lược, họ có thể phân tách các mô hình tái sử dụng vào các Bounded Contexts riêng biệt và thực hiện tích hợp khi thích hợp.
